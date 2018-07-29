import os # temporary for self.open until files.py or files/open.py, save.py, autosave.py implemented.

from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import save

__version__ = '0.0.1'


class MenuBar(object):
    """
    Install a menu on the given widget.
    """
    def __init__(self, widget):
        self.widget = widget
        for attr in 'edittabs', 'layout', '_parent':
            setattr(self, attr, getattr(widget, attr))
        self.setup_menu()

    def setup_menu(self):
        """
        Adds top menu bar and various menu items.
        """
        menu_bar = QtWidgets.QMenuBar(self.widget)
        file_menu = QtWidgets.QMenu('File')
        help_menu = QtWidgets.QMenu('Help')
        edit_menu = QtWidgets.QMenu('Edit')

        for menu in [file_menu, edit_menu, help_menu]:
            menu_bar.addMenu(menu)

        file_menu.addAction('New',
                            self.new)

        file_menu.addAction('Open',
                            self.open)

        file_menu.addAction('Save',
                            self.save)

        file_menu.addAction('Save As',
                            self.save_as)

        export_menu = QtWidgets.QMenu('Export')
        file_menu.addMenu(export_menu)
        ex = export_menu.addAction

        ex('Save Selected Text',
           self.save_selected_text)

        ex('Export Selected To External Editor',
           self.export_selected_to_external_editor)

        ex('Export Current Tab To External Editor',
           self.export_current_tab_to_external_editor)

        ex('Export All Tabs To External Editor',
           self.export_all_tabs_to_external_editor)

        help_menu.addAction('Reload Python Editor',
                            self._parent.reload_package)

        help_menu.addAction('About Python Editor',
                            self.show_about_dialog)

        edit_menu.addAction('Preferences',
                            self.show_preferences)

        edit_menu.addAction('Shortcuts',
                            self.show_shortcuts)

        self.layout().addWidget(menu_bar)

    @property
    def editor(self):
        return self.edittabs.currentWidget()

    def new(self):
        self.edittabs.new_tab()

    def open(self):
        """
        Simple open file.
        TODO: This needs to go into a files.py or files/open.py
        """
        o = QtWidgets.QFileDialog.getOpenFileName
        path, _ = o(self, "Open File")
        editor = self.edittabs.new_tab(tab_name=os.path.basename(path))
        editor.path = path

        # Because the document will be open in read-only mode, the
        # autosave will not save the editor's contents until the
        # contents have been modified.
        editor.read_only = True

        with open(path, 'rt') as f:
            editor.setPlainText(f.read())

    def save(self):
        save.save(self.editor)

    def save_as(self):
        save.save_as(self.editor)

    def save_selected_text(self):
        save.save_selected_text(self.editor)

    def export_selected_to_external_editor(self):
        save.export_selected_to_external_editor(self.editor)

    def export_current_tab_to_external_editor(self):
        save.export_current_tab_to_external_editor(self.edittabs)

    def export_all_tabs_to_external_editor(self):
        save.export_all_tabs_to_external_editor(self.edittabs)

    def show_shortcuts(self):
        """
        Generates a popup dialog listing available shortcuts.
        """
        self.widget.shortcuteditor.show()

    def show_preferences(self):
        """
        Generates a popup dialog listing available preferences.
        """
        self.widget.preferenceseditor.show()

    def show_about_dialog(self):
        """
        Shows an about dialog with version information.
        TODO: Make it a borderless splash screen, centred, nice text,
        major and minor version numbers set in one place in the
        project.
        """
        msg = 'Python Editor version {0} by Max Last'.format(__version__)
        self.about_dialog = QtWidgets.QLabel(msg)
        self.about_dialog.show()
