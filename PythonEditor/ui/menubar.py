
import os # temporary for self.open until files.py or files/open.py, save.py, autosave.py implemented.
import uuid
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import save
from PythonEditor.ui.features import actions
from PythonEditor._version import __version__


class MenuBar(object):
    """
    Install a menu on the given widget.
    """
    def __init__(self, widget):
        self.widget = widget
        self.tabeditor = widget.tabeditor
        self.tabs = widget.tabeditor.tabs
        self.editor = widget.tabeditor.editor
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

        file_menu.addAction(
            'New',
            self.new
        )

        file_menu.addAction(
            'Open',
            self.open
        )

        file_menu.addAction(
            '&Save',
            self.save
        )

        file_menu.addAction(
            'Save As',
            self.save_as
        )

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
                            self.widget._parent.reload_package)

        help_menu.addAction('About Python Editor',
                            self.show_about_dialog)

        # edit_menu.addAction('Preferences',
        #                     self.show_preferences)

        edit_menu.addAction('Shortcuts',
                            self.show_shortcuts)

        self.widget.layout().addWidget(menu_bar)

    def new(self):
        self.tabeditor.tabs.new_tab()

    def open(self):
        """
        Simple open file.
        """
        tabs = self.tabeditor.tabs
        editor = self.tabeditor.editor
        actions.open_action(tabs, editor)

    # TODO
    # The below methods and their counterparts in utils.save
    # need to have the API updated to reflect the new single editor.

    def save(self):
        tabs = self.tabeditor.tabs
        editor = self.editor
        actions.save_action(tabs, self.editor)

    def save_as(self):
        tabs = self.tabeditor.tabs
        tabs['path'] = ''
        editor = self.editor
        actions.save_action(tabs, self.editor)

    def save_selected_text(self):
        save.save_selected_text(self.editor)

    def export_selected_to_external_editor(self):
        save.export_selected_to_external_editor(self.editor)

    def export_current_tab_to_external_editor(self):
        save.export_current_tab_to_external_editor(self.tabs, self.editor)

    def export_all_tabs_to_external_editor(self):
        save.export_all_tabs_to_external_editor(self.tabs)

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
