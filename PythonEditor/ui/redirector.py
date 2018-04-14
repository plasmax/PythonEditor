import sys
import time
from Queue import Queue
from PythonEditor.ui.Qt import QtGui, QtWidgets, QtCore


class PySingleton(object):
    def __new__(cls, *args, **kwargs):
        if '_the_instance' not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


class Speaker(QtCore.QObject):
    """
    Used to relay sys stdout, stderr
    """
    emitter = QtCore.Signal(str)


class SERedirector(object):
    speaker = Speaker()

    def __init__(self, stream, queue=None):

        if hasattr(stream, 'saved_stream'):
            stream.reset()

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
                       '__iter__')

        for i in fileMethods:
            if not hasattr(self, i) and hasattr(stream, i):
                setattr(self, i, getattr(stream, i))

        self.saved_stream = stream
        self.queue = queue

    def write(self, text):
        self.queue.put(text)
        self.saved_stream.write(text)

    def close(self):
        self.flush()

    def stream(self):
        return self.saved_stream

    def __del__(self):
        self.reset()


class SESysStdOut(SERedirector, PySingleton):
    def reset(self):
        sys.stdout = self.saved_stream
        print 'reset stream out'


class SESysStdErr(SERedirector, PySingleton):
    def reset(self):
        sys.stderr = self.saved_stream
        print 'reset stream err'


class SESysStdIn(SERedirector, PySingleton):
    def reset(self):
        sys.stdin = self.saved_stream
        print 'reset stream in'


class Worker(QtCore.QObject):
    emitter = QtCore.Signal(str)

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, q):
        self._queue = q

    @QtCore.Slot()
    def run(self):
        while True:
            if not self._queue.empty():
                text = self._queue.get()
                self.emitter.emit(text)
                time.sleep(0.001)


class Terminal(QtWidgets.QTextBrowser):
    """ Output text display widget """
    def __init__(self):
        super(Terminal, self).__init__()
        self.setObjectName('Terminal')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setReadOnly(True)

        self.destroyed.connect(self.stop)
        self.setup_worker()

    def setup_worker(self):
        global queue
        self.worker = Worker()
        self.worker.emitter.connect(self.receive)
        self.worker.queue = queue
        self.worker_thread = QtCore.QThread(self)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    @QtCore.Slot(str)
    def receive(self, text):
        try:
            if bool(self.textCursor()):
                self.moveCursor(QtGui.QTextCursor.End)
        except Exception:
            pass
        self.insertPlainText(text)

    def stop(self):
        sys.stdout.reset()
        sys.stderr.reset()


queue = Queue()
sys.stdout = SESysStdOut(sys.stdout, queue)
sys.stderr = SESysStdErr(sys.stderr, queue)
sys.stdin = SESysStdIn(sys.stdin, queue)
