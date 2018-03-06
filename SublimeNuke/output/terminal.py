import sys
import Queue
try:
    import PySide
except:
    sys.path.append('C:/Users/Max-Last/.nuke/python/external')

from PySide import QtGui, QtCore
try:
    import hiero
except:
    pass

class StreamOut(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)
  
class StreamErr(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)
  
class Mexican(QtCore.QObject):
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

    def _setup(self):
        self.queue = Queue.Queue()
        
        self.old_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        sys.stdout = StreamOut(self.queue)

        self.old_stderr = sys.stderr
        sys.stderr = sys.__stderr__
        sys.stderr = StreamErr(self.queue)

        self.thread = QtCore.QThread(self)
        self.worker = Mexican(self.queue)
        self.worker.emitter.connect(self.receive)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.show()

    def _uninstall(self):
        """
        """
        if 'hiero' in globals():
            sys.stdin  = hiero.FnRedirect.SESysStdIn(sys.__stdin__)
            sys.stdout = hiero.FnRedirect.SESysStdOut(sys.__stdout__)
            sys.stderr = hiero.FnRedirect.SESysStdErr(sys.__stderr__)

        if hasattr(self, 'old_stdout'):
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr
            print 'hide!!'
            self.thread.terminate()
            self.worker.deleteLater()

    def hideEvent(self, event):
        self._uninstall()

    @QtCore.Slot(str)
    def receive(self, text):
        sys.__stdout__.write(text)
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(text)
        if 'hiero' in globals(): #write back to hiero FnRedirect (to be polite)
            self.old_stdout.write(text)