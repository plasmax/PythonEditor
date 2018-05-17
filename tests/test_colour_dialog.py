from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore

ide = [w for w in QtWidgets.QApplication.topLevelWidgets() if w.objectName() == 'IDE'][0]
ide.setStyleSheet('background:rgb(45,42,46);')

@QtCore.Slot(QtGui.QColor)
def info(colour):
    rgb = {'r': colour.red(),
               'g': colour.green(),
               'b': colour.blue()}
    ide.setStyleSheet('background:rgb({r},{g},{b});'.format(**rgb))

cd = QtWidgets.QColorDialog()
cd.currentColorChanged.connect(info)
#cd.colorSelected.connect(info)
cd.show()
