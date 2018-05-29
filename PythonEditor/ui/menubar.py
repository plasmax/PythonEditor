from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import save


class MenuBar(object):
    """
    Install a menu on the given widget.
    """
    def __init__(self, widget):
        self.widget = widget
        self.setup_menu(widget)

    def setup_menu(self, widget):
        menu_bar = QtWidgets.QMenuBar(widget)
        menu_bar.setMaximumHeight(30)
        file_menu = QtWidgets.QMenu('File')
        help_menu = QtWidgets.QMenu('Help')
        edit_menu = QtWidgets.QMenu('Edit')

        for menu in [file_menu, edit_menu, help_menu]:
            menu_bar.addMenu(menu)

        file_menu.addAction('Save',
                            self.save)

        file_menu.addAction('Save As',
                            self.save_as)

        file_menu.addAction('Save Selected Text',
                            self.save_selected_text)

        export_menu = QtWidgets.QMenu('Export')
        file_menu.addMenu(export_menu)

        export_menu.addAction('Selected To External Editor',
                              self.export_selected_to_external_editor)

        export_menu.addAction('Current Tab To External Editor',
                              self.export_current_tab_to_external_editor)

        export_menu.addAction('All Tabs To External Editor',
                              self.export_all_tabs_to_external_editor)

        # help_menu.addAction('Reload Python Editor',
        #                    self.parent.reload_package)

        edit_menu.addAction('Preferences',
                            self.show_preferences)

        edit_menu.addAction('Shortcuts',
                            self.show_shortcuts)

        self.widget.layout().addWidget(menu_bar)

    def save(self):
        cw = self.widget.tabs.currentWidget()
        save.save(cw)

    def save_as(self):
        cw = self.widget.tabs.currentWidget()
        save.save_as(cw)

    def save_selected_text(self):
        cw = self.widget.tabs.currentWidget()
        save.save_selected_text(cw)

    def export_selected_to_external_editor(self):
        cw = self.widget.tabs.currentWidget()
        save.export_selected_to_external_editor(cw)

    def export_current_tab_to_external_editor(self):
        save.export_current_tab_to_external_editor(self.widget.tabs)

    def export_all_tabs_to_external_editor(self):
        save.export_all_tabs_to_external_editor(self.widget.tabs)

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
