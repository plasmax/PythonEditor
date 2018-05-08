from PythonEditor.ui.Qt import QtCore, QtGui

QPalette = QtGui.QPalette
QBrush = QtGui.QBrush
QColor = QtGui.QColor


def getNukePalette():
    """
    #get macro for QApplication
    from PySide.QtGui import qApp
    #get palette
    nukePalette = qApp.palette()
    #apply palette
    myWindow.setPalette(nukePalette)

    else use the palette from below. Note that it is difficult to mix
    palettes and style sheets, it always gave me weird results.
    """
    palette = QPalette()

    brush = QBrush(QColor(255, 255, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.WindowText, brush)

    brush = QBrush(QColor(80, 80, 80))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Button, brush)

    brush = QBrush(QColor(75, 75, 75))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Light, brush)

    brush = QBrush(QColor(62, 62, 62))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Midlight, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Dark, brush)

    brush = QBrush(QColor(33, 33, 33))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Mid, brush)

    brush = QBrush(QColor(245, 245, 245))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Text, brush)

    brush = QBrush(QColor(255, 255, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.BrightText, brush)

    brush = QBrush(QColor(255, 255, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)

    brush = QBrush(QColor(58, 58, 58))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Base, brush)

    brush = QBrush(QColor(50, 50, 50))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Window, brush)

    brush = QBrush(QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Shadow, brush)

    brush = QBrush(QColor(247, 147, 30))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.Highlight, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush)

    brush = QBrush(QColor(255, 255, 220))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush)

    brush = QBrush(QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush)

    brush = QBrush(QColor(255, 255, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)

    brush = QBrush(QColor(80, 80, 80))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Button, brush)

    brush = QBrush(QColor(75, 75, 75))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Light, brush)

    brush = QBrush(QColor(62, 62, 62))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Dark, brush)

    brush = QBrush(QColor(33, 33, 33))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Mid, brush)

    brush = QBrush(QColor(245, 245, 245))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Text, brush)

    brush = QBrush(QColor(255, 255, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush)

    brush = QBrush(QColor(255, 255, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)

    brush = QBrush(QColor(58, 58, 58))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Base, brush)

    brush = QBrush(QColor(50, 50, 50))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Window, brush)

    brush = QBrush(QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)

    brush = QBrush(QColor(247, 147, 30))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush)

    brush = QBrush(QColor(255, 255, 220))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush)

    brush = QBrush(QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush)

    brush = QBrush(QColor(80, 80, 80))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Button, brush)

    brush = QBrush(QColor(75, 75, 75))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Light, brush)

    brush = QBrush(QColor(62, 62, 62))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Dark, brush)

    brush = QBrush(QColor(33, 33, 33))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Mid, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Text, brush)

    brush = QBrush(QColor(255, 255, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush)

    brush = QBrush(QColor(25, 25, 25))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)

    brush = QBrush(QColor(50, 50, 50))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Base, brush)

    brush = QBrush(QColor(50, 50, 50))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Window, brush)

    brush = QBrush(QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)

    brush = QBrush(QColor(174, 174, 174))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush)

    brush = QBrush(QColor(50, 50, 50))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush)

    brush = QBrush(QColor(255, 255, 220))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush)

    brush = QBrush(QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush)
    return palette
