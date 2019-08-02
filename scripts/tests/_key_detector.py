from Qt import QtWidgets, QtGui, QtCore, QtTest
import nukescripts
import json
import time


def get_action_dict():
    json_path = '/net/homes/mlast/Downloads/PythonEditor-master/PythonEditor/ui/features/action_register.json'

    with open(json_path, 'r') as f:
        action_dict = json.load(f)
    
    #print json.dumps(action_dict, indent=2)
    return action_dict
    

def get_shortcuts():
    action_dict = get_action_dict()
    shortcuts = []
    for widget_name, widget_actions in action_dict.items():
        for name, attributes in widget_actions.items():
            strokes = attributes['Shortcuts']
            for shortcut in strokes:
                shortcuts.append(str(shortcut))
    return shortcuts
    

#&&


modifier_map = {
    QtCore.Qt.Key_Control: QtCore.Qt.ControlModifier,
    QtCore.Qt.Key_Shift: QtCore.Qt.ShiftModifier,
    QtCore.Qt.Key_Alt: QtCore.Qt.AltModifier,
    #QtCore.Qt.Key_AltGr: QtCore.Qt.AltModifier,
    QtCore.Qt.Key.Key_Meta: QtCore.Qt.MetaModifier,
}


modifiers = {
    QtCore.Qt.ControlModifier  : QtCore.Qt.Key_Control,         
    QtCore.Qt.ShiftModifier    : QtCore.Qt.Key_Shift,       
    QtCore.Qt.AltModifier      : QtCore.Qt.Key_Alt,     
    #QtCore.Qt.AltModifier      : QtCore.Qt.Key_AltGr,     
    QtCore.Qt.MetaModifier     : QtCore.Qt.Key.Key_Meta,      
}



class Editor(QtWidgets.QPlainTextEdit):
    key_press_signal   = QtCore.Signal(QtGui.QKeyEvent)
    key_release_signal = QtCore.Signal(QtGui.QKeyEvent)
    def __init__(self):
        super(Editor, self).__init__()
        self.shortcut_manager = Shortcuts(self)
        global GLOBAL_EDITOR
        GLOBAL_EDITOR = self
        self.key_handled = False
        
    #def keyPressEvent(self, event):
        #self.key_handled = False
        ##self.key_press_signal.emit(event)
        ##if self.key_handled:
            ##return
        #super(Editor, self).keyPressEvent(event)
        
    #def keyReleaseEvent(self, event):
        #self.key_release_signal.emit(event)
        #super(Editor, self).keyReleaseEvent(event)
        
    def event(self, event):
        if not hasattr(event, 'key'):
            return super(Editor, self).event(event)
            
        if self.hasFocus():
            event.accept()
        else:
            event.ignore()
        
        #if self.key_handled:
            #return True
        if event.type() == QtCore.QEvent.KeyPress:
            self.key_handled = False
            self.key_press_signal.emit(event)
            if self.key_handled:
                self.key_handled = False
                return True
        if event.type() == QtCore.QEvent.KeyRelease:
            self.key_release_signal.emit(event)
            return True
        #self.key_handled = False
        return super(Editor, self).event(event)
        

class Shortcuts(object):
    def __init__(self, editor):
        self.editor = editor
        self.held_keys = []
        editor.key_press_signal.connect(
            self.handle_key_press,
            QtCore.Qt.DirectConnection
        )
        editor.key_release_signal.connect(
            self.handle_key_release,
            QtCore.Qt.DirectConnection
        )
        self.shortcuts = get_shortcuts()
    
    def handle_key_press(self, event):
        #self.editor.key_handled = True
        if event.isAutoRepeat():
            raise Exception('AutoRepeat')
            return
            
        if event.key() in modifier_map.keys():
            self.editor.key_handled = False
            return
        #key = event.key()
        # NEW
        curr = QtWidgets.QApplication.keyboardModifiers()
        modz = tuple( 
            which for ki, which in modifier_map.items() 
            #if curr | which == which 
            if curr & which == which 
        )
        print modz
        #for m, k in modifiers.items():
            #if m in event.modifiers():
        combo = 0
        for k in modz:
            combo |= k
        combo |= event.key()
        print event.key() == QtCore.Qt.Key_Down
        #QtCore.Qt.Key.values[QtCore.Qt.DownArrow
        #print event.key()

        # OLD
        """
        mod = modifier_map.get(key)
        if mod is not None:
            key = mod
        #stroke = QtGui.QKeySequence(event.key())
        #print stroke.toString()
        self.held_keys.append(key)
        
        combo = 0
        for key in self.held_keys:
            combo |= key
        """
            
        combo = str(QtGui.QKeySequence(combo).toString())

        global COMBO_FOUND
        COMBO_FOUND = False
        print repr(combo)
        if combo in self.shortcuts:
            event.accept()
            self.editor.key_handled = True
            for k, v in QtCore.Qt.Key.values.items():
                if v == event.key():
                    print v, 
                    break
            print combo
            COMBO_FOUND = True
            
            return
        self.editor.key_handled = False
    
    def handle_key_release(self, event):
        
        #if event.isAutoRepeat():
            #return
        if event.modifiers() == QtCore.Qt.NoModifier:
            self.held_keys = []
            return
            ##raise Exception('EMPTYING KEYS')
            #print 'EMPTYING KEYS'
        #key = event.key()
        #mod = modifier_map.get(key)
        #if mod is not None:
            #key = mod
        #if key in self.held_keys:
            #self.held_keys.remove(key)


#&&

e = Editor()
e.show()
GLOBAL_EDITOR = e

#&&

nukescripts.registerWidgetAsPanel(
    'Editor', 
    'shortcuts', 
    'id', 
    create=True
)

#&&


def test_shortcuts():
    GLOBAL_EDITOR.setFocus(
        QtCore.Qt.MouseFocusReason
    )
    if not GLOBAL_EDITOR.hasFocus():
        raise Exception(
            'Need an editor visible to test'
        )
        
    shortcuts = get_shortcuts()
    for shortcut in shortcuts:
        modifiers = QtCore.Qt.NoModifier
        shortcut = shortcut.strip()

        seq = shortcut.split('+')
        if shortcut.endswith('+'):
            letter = '+'
        for part in seq:
            part = part.strip()
            if not part:
                continue
            if part.lower()   == 'ctrl':
                modifiers |= QtCore.Qt.ControlModifier
            elif part.lower() == 'shift':
                modifiers |= QtCore.Qt.ShiftModifier
            elif part.lower() == 'alt':
                modifiers |= QtCore.Qt.AltModifier
            elif part.lower() == 'meta':
                modifiers |= QtCore.Qt.MetaModifier
            else:
                # only allow one part for now
                letter = part
            
        # find the relevant key for the part
        if letter == 'Del':
            letter = 'Delete'
        lookup = 'Key_'+letter
        ky = QtCore.Qt.Key.values.get(lookup)
        if ky is None:
            ky = QtTest.QTest.asciiToKey(letter)
            print 'failed to find %s, using %s' % (lookup, ky)
    
        combo = ky | modifiers
        print '#----------------------'
        print QtGui.QKeySequence(combo).toString()
        print '\nTesting:', shortcut, ky

        GLOBAL_EDITOR.setFocus(
            QtCore.Qt.MouseFocusReason
        )
        QtTest.QTest.keyPress(
            GLOBAL_EDITOR,
            ky,
            modifiers    
        )
        GLOBAL_EDITOR.setFocus(
            QtCore.Qt.MouseFocusReason
        )
        #time.sleep(0.01)
        #QtTest.QTest.keyRelease(
            #GLOBAL_EDITOR,
            #ky,
            #modifiers
            #QtCore.Qt.NoModifier
        #)
        print '#------------', 
        if not COMBO_FOUND:
            print 'KEY NOT WORKING!'
            raise Exception('KEY NOT WORKING!')
        else:
            print 'passed.'
        yield
        

g = test_shortcuts()
#g.next()
list(g)
    
#&&
# Ctrl+=

GLOBAL_EDITOR.setFocus(
    QtCore.Qt.MouseFocusReason
)
QtTest.QTest.keyPress(
    GLOBAL_EDITOR,
    QtCore.Qt.Key.Key_Equal,
    QtCore.Qt.ControlModifier
)
print COMBO_FOUND

#&&
GLOBAL_EDITOR.setFocus(
    QtCore.Qt.MouseFocusReason
)
QtTest.QTest.keyPress(
    GLOBAL_EDITOR,
    QtCore.Qt.Key.Key_Down,
    QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.AltModifier
)
print COMBO_FOUND

'Ctrl+Alt+Shift+Down' in get_shortcuts()
