

def connect(cls, signal, slot):
    """
    Function to connect signals to slots and get the signature
    of the signal in the process, i.e. "2signal(PyObject)"

    TODO: instead of using a global temp variable,
    a variable on the given class may work better.
    """
    global __temp_name
    __temp_name = 'temp'

    def foo(x):
        global __temp_name
        __temp_name = x

    connectNotify = cls.connectNotify
    cls.connectNotify = foo
    signal.connect(slot)
    cls.connectNotify = connectNotify
    name = __temp_name
    del __temp_name
    return name, signal, slot
