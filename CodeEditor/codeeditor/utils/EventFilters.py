import sys
import traceback
from codeeditor.ui.Qt import QtGui, QtCore, QtWidgets

def full_stack():
    """
    Print full stack information from error within try/except block.
    """
    import traceback, sys
    exc = sys.exc_info()[0]
    if exc is not None:
        f = sys.exc_info()[-1].tb_frame.f_back
        stack = traceback.extract_stack(f)
    else:
        stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
        stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

class GenericEventFilter(QtCore.QObject):
    """
    Generic EventFilter
    Implements safe filtering with auto-installation 
    and autoquit with full stack trace on error.

    example usage:
    from EventFilters import GenericEventFilter
    class Filt(GenericEventFilter):
        def event_filter(self, obj, event):
            1/0 #cause error

    filt = Filt()

    """
    def __init__(self, target=None):
        super(GenericEventFilter, self).__init__()
        self.setObjectName('GenericEventFilter')

        if target is None:
            target = QtWidgets.QApplication.instance()

        self.target = target
        QtCore.QCoreApplication.installEventFilter(self.target, self)

    def eventFilter(self, obj, event):
        if (event.type() == QtCore.QEvent.KeyPress
            and event.key() == QtCore.Qt.Key_Escape):
                self.quit()
                return True
        try:
            return self.event_filter(obj, event)
        except:
            self.quit()
            print full_stack()
            return True
        else:
            return False

    def event_filter(self, obj, event):
        return False

    def quit(self):
        print self.__class__, 'exiting'
        QtCore.QCoreApplication.removeEventFilter(self.target, self)
        self.deleteLater()

class InfoFilter(GenericEventFilter):
    """
    Example Filter that prints object and event information.
    """
    def event_filter(self, obj, event):
        print obj.metaObject().className(), event.type()
        return False

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    f = SimpleFilter(target=w)
    w.show()
    app.exec_()
    
