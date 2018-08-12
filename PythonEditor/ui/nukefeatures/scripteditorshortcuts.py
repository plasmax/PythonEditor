
from PythonEditor.utils.eventfilters import GenericEventFilter
from PythonEditor.ui.Qt import QtCore, QtWidgets


class ScriptEditorShortcuts(GenericEventFilter):
    """
    Accept shortcuts executed in the Script Editor
    to stop them from being overridden by Python Editor.
    """
    def event_filter(self, obj, event):
        #try:
        types = [
            QtCore.QEvent.KeyRelease,
            QtCore.QEvent.KeyPress,
            QtCore.QEvent.Shortcut,
            QtCore.QEvent.ShortcutOverride,
        ]
        if event.type() not in types:
            return False # eventfilter does nothing
            
        mo = obj.metaObject().className()
        script_input = 'Foundry::PythonUI::ScriptInputWidget'
        script_output = 'Foundry::PythonUI::ScriptOutputWidget'
        
        if mo in (script_input, script_output):
            event.accept()
        #except Exception:
            #pass
        return False
      
          
filt = ScriptEditorShortcuts()
