from __future__ import print_function
import sys
from queue import Queue
from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui

_QUEUE = Queue()
STEAL_OUTPUT = True


class PySingleton(object):
    def __new__(cls, *args, **kwargs):
        if '_the_instance' not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


class SERedirector(object):
    def __init__(self, stream):
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

        self.savedStream = stream

    def write(self, text):
        if STEAL_OUTPUT:
            _QUEUE.put(text)
        else:
            # queue up a maximum
            # for when output opens
            if _QUEUE.qsize() > 10000:
                with _QUEUE.mutex:
                    _QUEUE.queue.clear()

            _QUEUE.put(text)
            self.savedStream.write(text)

    def close(self):
        self.flush()

    def stream(self):
        return self.savedStream

    def __del__(self):
        self.reset()


class SESysStdOut(SERedirector, PySingleton):
    def reset(self):
        sys.stdout = self.savedStream
        print('reset stream out')


class SESysStdErr(SERedirector, PySingleton):
    def reset(self):
        sys.stderr = self.savedStream
        print('reset stream err')

    # def write(self, text):
    #     if is_path:
    #         pass # write html here or put into HTML queue

    #     if STEAL_OUTPUT:
    #         _QUEUE.put(text)
    #     else:
    #         # queue up a maximum
    #         # for when output opens
    #         if _QUEUE.qsize() > 10000:
    #             with _QUEUE.mutex:
    #                 _QUEUE.queue.clear()

    #         _QUEUE.put(text)
    #         self.savedStream.write(text)


class Worker(QtCore.QRunnable):
    def __init__(self, parent):
        super(Worker, self).__init__()
        self.parent = parent
        self.active = True

    def run(self):
        while True:
            if self.active:
                global _QUEUE
                if not _QUEUE.empty():
                    text = _QUEUE.get()
                    self.parent.append_output(text)


class Output(QtWidgets.QPlainTextEdit):
    """
    Logger widget for python output
    If visible, has a timer running that
    collects from queue.
    """
    def __init__(self, ):
        super(Output, self).__init__()
        self.setStyleSheet('background:rgb(45,42,46);')

        self.setObjectName('Output')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setReadOnly(True)

        # self.destroyed.connect(self.stop)
        # self.setup_timer()
        self.setup_thread()

    def setup_thread(self):
        self.pool = QtCore.QThreadPool.globalInstance()
        self.worker = Worker(self)
        self.pool.start(self.worker)

    def setup_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.q_pull)

    @QtCore.Slot()
    def q_pull(self):
        global _QUEUE
        if not _QUEUE.empty():
            text = _QUEUE.get()
            self.append_output(text)

    def append_output(self, text):
        try:
            textCursor = self.textCursor()
            if bool(textCursor):
                self.moveCursor(QtGui.QTextCursor.End)
        except Exception:
            pass
        self.insertPlainText(text)
        # self.appendHtml(text)

    def showEvent(self, e):
        global STEAL_OUTPUT
        STEAL_OUTPUT = True
        self.worker.active = True
        # self.timer.start()
        super(Output, self).showEvent(e)

    def hideEvent(self, e):
        global STEAL_OUTPUT
        STEAL_OUTPUT = False
        self.worker.active = False
        # self.timer.stop()
        super(Output, self).hideEvent(e)

def setup():
    for stream in sys.stdout, sys.stderr, sys.stdin:
        if hasattr(stream, 'reset'):
            reset = getattr(stream, 'reset')
            reset()

    sys.stdout = SESysStdOut(sys.stdout)
    sys.stderr = SESysStdErr(sys.stderr)

setup()
