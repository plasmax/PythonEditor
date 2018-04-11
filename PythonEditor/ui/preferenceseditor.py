import os
from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui
from PythonEditor.utils.constants import set_external_editor_path

class PreferencesEditor(QtWidgets.QTreeView):
    """
    A display widget that allows editing of
    preferences assigned to the editor.
    TODO: Implement mechanism to change external editor.
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

        #TODO: connect externaleditorpath text changed signal (or set prefs on preferences > close?)

    def showEvent(self, event):
        self.show_current_preferences()
        super(PreferencesEditor, self).showEvent(event)

    def show_current_preferences(self):
        self.externalEditorPath.setText(unicode(os.environ.get('EXTERNAL_EDITOR_PATH')))
