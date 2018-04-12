from functools import partial
import nuke
from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui

class PyKnobEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, knob):
        super(PyKnobEdit, self).__init__()
        self._knob = knob
        self.setPlainText(knob.value())
        self.textChanged.connect(self.updateValue)

    def updateValue(self):
        #prepend = "if nuke.thisKnob().name() != 'knobChanged':"
        self._knob.setValue(self.toPlainText())        

@QtCore.Slot(object)
def addTextKnobs(node):
    print node.name()

    np_list = [w for w in QtWidgets.QApplication.instance().allWidgets()
               if w.objectName() == node.name()]
    if len(np_list) > 0:
        np = np_list.pop()
    else:
        return
        
    sw = np.findChild(QtWidgets.QStackedWidget, 'qt_tabwidget_stackedwidget')
    print sw
    tw = sw.parent()
    stw = QtWidgets.QTabWidget() # probably nicer to have a dropdown connected to a single textedit
    tw.addTab(stw, 'Python Knobs')

    for k in node.allKnobs():
        if 'py' in k.Class().lower():
            stw.addTab(PyKnobEdit(k), k.name())

def pythonKnobEdit():
    if nuke.thisKnob().name() == 'showPanel':
        node = nuke.thisNode()
        global timer
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(10)
        timer.timeout.connect( partial(addTextKnobs, node) )
        #timer.timeout.connect(lambda n=node:addTextKnobs(node) )
        timer.start()


testing = """
nuke.pluginAddPath('/net/homes/mlast/.nuke/python/max/gear/tools/')

import M_PyKnobPanel
reload(M_PyKnobPanel)

del nuke.callbacks.knobChangeds['*'][1]
"""

nuke.callbacks.addKnobChanged(pythonKnobEdit, args=(), kwargs={}, nodeClass='*', node=None)
