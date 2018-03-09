import sys
try:
    from PySide import QtGui, QtCore
except ImportError:
    try:
        sys.path.append('/usr/lib64/python2.7/site-packages/')
        from PyQt4 import QtGui, QtCore
        QtCore.Signal = QtCore.pyqtSignal
        QtCore.Slot = QtCore.pyqtSlot
    except ImportError:
        sys.path.append('C:/Program Files/Nuke10.5v1/pythonextensions/site-packages')
        from PySide import QtGui, QtCore
