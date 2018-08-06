from PySide import QtGui, QtCore

class Window(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        widget = QtGui.QWidget(self)
        self.setCentralWidget(widget)
        layout = QtGui.QVBoxLayout(widget)
        self.edit = QtGui.QTextEdit(self)
        self.edit.setText('text')
        self.table = Table(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.table)
        menu = self.menuBar().addMenu('&File')
        def add_action(text, shortcut):
            action = menu.addAction(text)
            action.setShortcut(shortcut)
            action.triggered.connect(self.handleAction)
            action.setShortcutContext(QtCore.Qt.WidgetShortcut)
            self.edit.addAction(action)
        add_action('&Copy', 'Ctrl+C')
        add_action('&Print', 'Ctrl+P')

    def handleAction(self):
        print ('Action!')

class Table(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self, parent)
        self.setRowCount(4)
        self.setColumnCount(2)
        self.setItem(0, 0, QtGui.QTableWidgetItem('item'))

    def keyPressEvent(self, event):
        print ('keyPressEvent: %s' % event.key())
        QtGui.QTableWidget.keyPressEvent(self, event)

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
