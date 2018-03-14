import os
import sys
import Queue
import time
from pprint import pprint
import inspect
print 'importing', __name__, 'at', time.asctime()

from ..qt import QtGui, QtCore

class PySingleton(object):
    def __new__(cls, *args, **kwargs):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance

class SERedirector(object):
    def __init__(self, stream, sig=None):
        fileMethods = ('fileno', 'flush', 'isatty', 'read', 'readline', 'readlines',
        'seek', 'tell', 'write', 'writelines', 'xreadlines', '__iter__')

        for i in fileMethods:
            if not hasattr(self, i) and hasattr(stream, i):
                setattr(self, i, getattr(stream, i))

        self.savedStream = stream
        self.sig = sig

    def write(self, text):
        if self.sig != None:
            self.sig.emitter.emit(text)
        self.savedStream.write(text)

    def close(self):
        self.flush()

    def stream(self):
        return self.savedStream

    def reset(self):
        pass

    def __del__(self):
        self.reset()

class SESysStdOut(SERedirector, PySingleton):
    def reset(self):
        sys.stdout = self.savedStream
        print 'reset stream out'
        

class SESysStdErr(SERedirector, PySingleton):
    def reset(self):
        sys.stderr = self.savedStream
        print 'reset stream err'

class Speaker(QtCore.QObject):
    emitter = QtCore.Signal(str)

class Terminal(QtGui.QTextEdit):
    def __init__(self):
        super(Terminal, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setReadOnly(True)
        self.setup()
        self.destroyed.connect(self.stop)

    @QtCore.Slot(str)
    def receive(self, text):
        self.insertPlainText(text)
        try:
            if bool(self.textCursor()):
                self.moveCursor(QtGui.QTextCursor.End)
        except Exception, e:
            pass

    def stop(self):
        sys.stdout.reset()
        sys.stderr.reset()

    def setup(self):
        """
        To stop:
        runner.shouldRun = False

        To connect:
        speaker.emitter.connect(recv)

        """

        if hasattr(sys.stdout, 'sig'):
            speaker = sys.stdout.sig
        else:
            speaker = Speaker()
            sys.stdout = SESysStdOut(sys.stdout, speaker)
            sys.stderr = SESysStdErr(sys.stderr, speaker)

        speaker.emitter.connect(self.receive)
