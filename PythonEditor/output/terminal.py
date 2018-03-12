import os
import sys
import Queue
import time
from pprint import pprint
import inspect
print 'importing', __name__, 'at', time.asctime()

from qt import QtGui, QtCore

try:
    import hiero
except ImportError:
    print 'could not import hiero'

class FnPySingleton(object):
    def __new__(type, *args, **kwargs):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        else:
            print type._the_instance, 'already exists'
        return type._the_instance

class StreamOut(FnPySingleton):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)
  
class StreamErr(FnPySingleton):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)
  
class Worker(QtCore.QObject, FnPySingleton):
    emitter = QtCore.Signal(str)
    def __init__(self, queue, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.queue = queue

    @QtCore.Slot()
    def run(self):
        while True:
            text = self.queue.get()
            self.emitter.emit(text)

class Terminal(QtGui.QTextEdit):
    def __init__(self):
        super(Terminal, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setReadOnly(True)

    def _setup(self):
        self.queue = Queue.Queue()
        
        self.old_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        sys.stdout = StreamOut(self.queue)

        self.old_stderr = sys.stderr
        sys.stderr = sys.__stderr__
        sys.stderr = StreamErr(self.queue)

        self.thread = QtCore.QThread(self)
        self.worker = Worker(self.queue)
        self.worker.emitter.connect(self.receive)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.show()

    def _uninstall(self):
        """
        """

        # caller_globals = dict(inspect.getmembers(inspect.stack()[1][0]))['f_globals']
        # pprint(caller_globals)
        # pprint(inspect.stack())
        if 'nuke' in caller_globals:
            sys.stdin  = hiero.FnRedirect.SESysStdIn(sys.__stdin__)
            sys.stdout = hiero.FnRedirect.SESysStdOut(sys.__stdout__)
            sys.stderr = hiero.FnRedirect.SESysStdErr(sys.__stderr__)
            print 'hiero'
            nuke.tprint('hiero')

        elif hasattr(self, 'old_stdout'):
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr
            print 'reassign stdout and quit'
            self.thread.quit()
            self.thread.terminate()
            # if not 'nuke' in globals(): self.thread.wait()
            self.worker.deleteLater()

    @QtCore.Slot(str)
    def receive(self, text):
        sys.__stdout__.write(text)
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(text)
        if 'hiero' in globals(): #write back to hiero FnRedirect (to be polite)
            self.old_stdout.write(text)

    @QtCore.Slot()
    def clearInput(self):
        self.clear()
