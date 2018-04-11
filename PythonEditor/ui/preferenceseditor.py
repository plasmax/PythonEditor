from Qt import QtWidgets, QtCore, QtGui

class PreferencesEditor(QtWidgets.QTreeView):
    """
    A display widget that allows editing of
    preferences assigned to the editor.
    """
    def __init__(self):
        super(PreferencesEditor, self).__init__()
        self.setObjectName('PythonEditorPreferences')
        self.layout = QtWidgets.QVBoxLayout(self)

        self.externalEditorPath = QtWidgets.QLineEdit()
        self.externalEditorLabel = QtWidgets.QLabel('External Editor Path')
        self.externalEditorLabel.setBuddy(self.externalEditorPath)
        self.layout.addWidget(self.externalEditorLabel)
        self.layout.addWidget(self.externalEditorPath)
