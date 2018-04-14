import os
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import constants


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

        self.editPath = QtWidgets.QLineEdit()
        self.externalEditorLabel = QtWidgets.QLabel('External Editor Path')
        self.externalEditorLabel.setBuddy(self.editPath)
        self.layout.addWidget(self.externalEditorLabel)
        self.layout.addWidget(self.editPath)

        self.editPath.editingFinished.connect(self.set_editor_path)

    def set_editor_path(self):
        path = self.editPath.text()
        constants.set_external_editor_path(path=path)

    def showEvent(self, event):
        self.show_current_preferences()
        super(PreferencesEditor, self).showEvent(event)

    def show_current_preferences(self):
        self.editPath.setText(unicode(os.environ.get('EXTERNAL_EDITOR_PATH')))
