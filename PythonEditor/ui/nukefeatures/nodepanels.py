from functools import partial
import nuke
from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui
from PythonEditor.ui import editor

class PyKnobs(QtWidgets.QWidget):
    """docstring for PyKnobs"""
    def __init__(self, knobs):
        super(PyKnobs, self).__init__()
        self.knobs = knobs
        self._knob = knobs[0]
        self.layout = QtWidgets.QVBoxLayout(self)

        self.knobChooser = QtWidgets.QComboBox()
        self.knobChooser.addItems([k.name() for k in knobs])
        self.editor = PyKnobEdit(self._knob)

        self.layout.addWidget(self.knobChooser)
        self.layout.addWidget(self.editor)

        self.knobChooser.currentIndexChanged.connect(self.updateKnob)

    def updateKnob(self, index):
        self.editor.knob = self.knobs[index]
        self.editor.getKnobValue()

class PyKnobEdit(editor.Editor):
    """
    Editor that automatically updates knobs.
    """
    def __init__(self, knob):
        super(PyKnobEdit, self).__init__()
        self._knob = knob
        self.textChanged.connect(self.updateValue)

    def updateValue(self):
        # if self._knob.name() != 'knobChanged':
        self._knob.setValue(self.toPlainText())

    def hideEvent(self, event):
        super(PyKnobEdit, self).hideEvent(event)

    @property
    def knob(self):
        return self._knob

    @knob.setter
    def knob(self, knob):
        self._knob = knob
        
    def getKnobValue(self):
        self.setPlainText(self.knob.value())

@QtCore.Slot(object)
def addTextKnobs(node):
    """
    Finds node panel widget and adds some 
    extra widgets to it that act like knobs.
    TODO: find node panels in Properties bin.
    also appears that this causes segmentation faults
    probably because of pointers to missing or already deleted widgets.
    """
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
    pyk = PyKnobs([k for k in node.allKnobs() if 'py' in k.Class().lower()])
    tw.addTab(pyk, 'Python Knobs')
    
    # stw = QtWidgets.QTabWidget() #TODO: probably nicer to have a dropdown connected to a single textedit
    # tw.addTab(stw, 'Python Knobs')

    # for k in node.allKnobs():
    #     if 'py' in k.Class().lower():
    #         stw.addTab(PyKnobEdit(k), k.name())

def pythonKnobEdit():
    if nuke.thisKnob().name() == 'showPanel': #TODO: is there a 'knob added' knobchanged?
        node = nuke.thisNode()
        global timer
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(10)
        timer.timeout.connect( partial(addTextKnobs, node) )
        #timer.timeout.connect(lambda n=node:addTextKnobs(node) )
        timer.start()


testing = """
from PythonEditor.ui.nukefeatures import nodepanels
reload(nodepanels)

#to delete
del nuke.callbacks.knobChangeds['*'][1]
"""

knobChangeds = nuke.callbacks.knobChangeds['*']
for index, info in enumerate(knobChangeds):
    func, _,_,_ = info
    if func.func_name == 'pythonKnobEdit':
        del knobChangeds[index]

nuke.callbacks.addKnobChanged(pythonKnobEdit, args=(), kwargs={}, nodeClass='*', node=None)
