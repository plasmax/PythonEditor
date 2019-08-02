# capture keystrokes including modifiers and turn them into human-readable format
from Qt import QtCore, QtWidgets, QtGui


def is_int(key):
    try:
        int(key)
        return True
    except Exception:
        return False

def is_key(key):
    return ('key' in repr(key).lower())
    
modmap = {
        QtCore.Qt.Key_Control: QtCore.Qt.ControlModifier,
        QtCore.Qt.Key_Shift: QtCore.Qt.ShiftModifier,
        QtCore.Qt.Key_Alt: QtCore.Qt.AltModifier,
        QtCore.Qt.Key.Key_Meta: QtCore.Qt.MetaModifier,
}
#keymap = {v:v for k,v in QtCore.Qt.__dict__.items() if is_key(v) and is_int(v)}
#keymap.update(**modmap)

class Captcha(QtWidgets.QLineEdit):
    keylist = []
    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        key = modmap.get(key, key)

        self.keylist.append(key)
        combo = 0
        text = ''
        for k in self.keylist:
            if k in modmap.values():
                combo |= k
            else:
                if text != '':
                    text += '+'
                text += QtGui.QKeySequence(k).toString()

        stroke = QtGui.QKeySequence(combo).toString()
        self.setText(stroke+text)
    
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        key = modmap.get(key, key)
        try:
            self.keylist.remove(key)
        except ValueError:
            pass


if __name__ == '__main__':
    captcha = Captcha()
    captcha.show()
