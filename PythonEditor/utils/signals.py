

def connect(cls, signal, slot):
    global __super_temp_name
    __super_temp_name = 'banana'

    def foo(x):
        global __super_temp_name
        __super_temp_name = x

    connectNotify = cls.connectNotify
    cls.connectNotify = foo
    signal.connect(slot)
    cls.connectNotify = connectNotify
    name = __super_temp_name
    del __super_temp_name
    return name, signal, slot
