import sys, os
from PySide import QtGui, QtCore
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class Nuke(QtGui.QMainWindow):
    """
    Natron Usage:
    sys.path.append('C:/Repositories/PythonEditor/tests')
    import nuke
    import nukescripts
    sys.path.append('C:/Repositories/PythonEditor/')
    import PythonEditor
    import NukeApp
    nukeApp = NukeApp.Nuke()
    nukeApp.show()
    """
    def __init__(self):
        super(Nuke, self).__init__()
        self.setWindowTitle('Nuke')
        self.resize(300, 400)
        # self.setStyleSheet('color: #000000;'\
            # 'background: #3e3e3e;')
        #create Nuke menu
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 662, 28))
        self.menubar.setObjectName("MenuBar")
        for name in ['Nuke', 'Pane', 'Nodes']:
            menu = QtGui.QMenu(self.menubar)
            menu.setObjectName(name)
            menu.setTitle(
                QtGui.QApplication.translate(
                            "MainWindow", 
                            name, 
                            None, 
                            QtGui.QApplication.UnicodeUTF8))

            self.menubar.addAction(menu.menuAction())
        
        #     self.menuMenu = QtGui.QMenu(self.menubar)
        #     self.menuMenu.setObjectName("Pane")
        #     self.menuMenu.setTitle(
        #         QtGui.QApplication.translate(
        #                     "MainWindow", 
        #                     "Pane", 
        #                     None, 
        #                     QtGui.QApplication.UnicodeUTF8))

        # self.menubar.addAction(self.menuMenu.menuAction())

        # self.menuMenu.addAction('Load Python Editor', self.load)

        self.setMenuBar(self.menubar)

        # create docks
        dock1 = QtGui.QDockWidget()
        dock1.setObjectName('Dock1')
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock1)

        dock2 = QtGui.QDockWidget()
        dock2.setObjectName('Dock2')
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock2)

        self.tabifyDockWidget(dock1, dock2)

        self.load()

    def load(self):
        import PythonEditor
        PythonEditor.main()

def main():
    app = QtGui.QApplication(sys.argv)
    nuke = Nuke()
    nuke.show()

    import qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    app.exec_()
    
if __name__ == '__main__':
    sys.exit(main())