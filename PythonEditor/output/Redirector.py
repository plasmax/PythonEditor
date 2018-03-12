import sys
import Queue
from qt import QtGui, QtCore

class Terminal(QtGui.QTextEdit):
    def __init__(self):
        super(Terminal, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setReadOnly(True)
        threadmanager.worker.emitter.connect(self.receive)
        self.destroyed.connect(threadmanager.thread.quit)

    @QtCore.Slot()
    def receive(self, text):
        self.insertPlainText(text)
        try:
            if bool(self.textCursor()):
                self.moveCursor(QtGui.QTextCursor.End)
        except Exception, e:
            pass

class PySingleton(object):
    def __new__(cls, *args, **kwargs):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance

class SERedirector(object):
    def __init__(self, stream, queue):
        fileMethods = ('fileno', 'flush', 'isatty', 'read', 'readline', 'readlines',
        'seek', 'tell', 'write', 'writelines', 'xreadlines', '__iter__')

        for i in fileMethods:
            if not hasattr(self, i) and hasattr(stream, i):
                setattr(self, i, getattr(stream, i))

        self.queue = queue
        self.savedStream = stream

    def write(self, text):
        self.queue.put(text)
        self.savedStream.write(text)

    def close(self):
        self.flush()

    def stream(self):
        return self.savedStream

    def reset(self):
        pass

    def __del__(self):
        self.reset()

class QtSingleton(QtCore.QObject):
    def __new__(cls, *args, **kwargs):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance =  QtCore.QObject.__new__(cls)
        return cls._the_instance

    def __init__(self, *args, **kwargs):
        if not '_the_instance' in self.__dict__:
            QtCore.QObject.__init__(self, *args, **kwargs)

class Worker(QtSingleton):
    emitter = QtCore.Signal(str)

    def __init__(self):
        super(Worker, self).__init__()
  
    @property
    def queue(self):
        return self._queue
    
    @queue.setter
    def queue(self, q):
        self._queue = q

    @QtCore.Slot()
    def run(self):
        while True:
            text = self._queue.get()
            self.emitter.emit(text)

class SESysStdOut(SERedirector, PySingleton):
    def reset(self):
        sys.stdout = self.savedStream
        print 'reset stream out'
        

class SESysStdErr(SERedirector, PySingleton):
    def reset(self):
        sys.stderr = self.savedStream
        print 'reset stream err'

class ThreadManager(QtSingleton):
    def __init__(self):
        super(ThreadManager, self).__init__()
        
        self.queue = Queue.Queue()
        self.worker = Worker()
        self.worker.queue = self.queue
        self.thread = QtCore.QThread(self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.setup()

    def setup(self):
        for _stream in [sys.stdout, sys.stderr]:
            if hasattr(_stream, 'reset'):
                _stream.reset()
            
        sys.stdout = SESysStdOut(sys.stdout, self.queue)
        sys.stderr = SESysStdErr(sys.stderr, self.queue)

optional_module_exec = """
queue = Queue.Queue()

worker = Worker()
worker.queue = queue
thread = QtCore.QThread()
worker.moveToThread(thread)
thread.started.connect(worker.run)
thread.start()

def setup():
    for _stream in [sys.stdout, sys.stderr]:
        if hasattr(_stream, 'reset'):
            _stream.reset()
        
    sys.stdout = SESysStdOut(sys.stdout, queue)
    sys.stderr = SESysStdErr(sys.stderr, queue)

setup()
"""
threadmanager = ThreadManager()