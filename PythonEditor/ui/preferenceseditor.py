import os
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import constants


class PreferencesEditor(QtWidgets.QDialog):
    """
    A display widget that allows editing of
    preferences assigned to the editor.
    TODO: Implement mechanism to change external editor.
    """
    def __init__(self):
        super(PreferencesEditor, self).__init__()
        self.setObjectName('PythonEditorPreferences')
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setWindowTitle('Python Editor Preferences')

        self.build_layout()
        self.connect_signals()

    def build_layout(self):

        # external editor path
        self.edit_path = QtWidgets.QLineEdit()
        self.external_editor_label = QtWidgets.QLabel('External Editor Path')
        self.external_editor_label.setBuddy(self.edit_path)
        self.layout.addWidget(self.external_editor_label)
        self.layout.addWidget(self.edit_path)

        # # change editor colours
        self.choose_colour_button = QtWidgets.QPushButton('Choose Colour')
        self.colour_dialog = QtWidgets.QColorDialog()
        self.choose_colour_button.clicked.connect(self.colour_dialog.show)
        self.layout.addWidget(self.choose_colour_button)

        # change editor font
        self.font_size = QtWidgets.QSpinBox()
        self.font_size.setValue(9)
        self.font_size_label = QtWidgets.QLabel('Choose Font Size')
        self.font_size_label.setBuddy(self.font_size)
        self.layout.addWidget(self.font_size_label)
        self.layout.addWidget(self.font_size)

    def connect_signals(self):
        self.edit_path.editingFinished.connect(self.set_editor_path)

    def set_editor_path(self):
        path = self.edit_path.text()
        constants.set_external_editor_path(path=path)

    def showEvent(self, event):
        self.show_current_preferences()
        super(PreferencesEditor, self).showEvent(event)

    def show_current_preferences(self):
        self.edit_path.setText(unicode(os.environ.get('EXTERNAL_EDITOR_PATH')))
