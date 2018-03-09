try:
    from PySide import QtGui, QtCore
except ImportError, e:
    import sys
    try:
        print e, ', trying nuke PySide installation'
        sys.path.append('/opt/foundry/nuke-10.0v4/pythonextensions/site-packages/')
        from PySide import QtGui, QtCore
        print QtGui, QtCore
    except ImportError:
        try:
            print e, ', defaulting to PyQt'
            sys.path.append('/usr/lib64/python2.7/site-packages/')
            from PyQt4 import QtGui, QtCore
            QtCore.Signal = QtCore.pyqtSignal
            QtCore.Slot = QtCore.pyqtSlot
        except ImportError:
            print e, ', trying windows nuke PySide installation'
            sys.path.append('C:/Program Files/Nuke10.5v1/pythonextensions/site-packages')
            from PySide import QtGui, QtCore
