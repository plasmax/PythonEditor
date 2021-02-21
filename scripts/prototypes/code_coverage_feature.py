# code coverage feature for pythoneditor - this would be AMAZING on a "record" button!

# basically, all your integration testing now also becomes code coverage testing...


import sys


# def displayhook(value):
    # print('displayhook:', value)
# sys.displayhook = displayhook
# sys.displayhook = sys.__displayhook__


def get_class_from_frame(fr):
  import inspect
  args, _, _, value_dict = inspect.getargvalues(fr)
  # we check the first parameter for the frame function is
  # named 'self'
  if len(args) and args[0] == 'self':
    # in that case, 'self' will be referenced in value_dict
    instance = value_dict.get('self', None)
    if instance:
      # return its class
      return getattr(instance, '__class__', None)
  # return None otherwise
  return None


class Trace(object):
    def __init__(self, module_name):
        self.module_name = module_name
        self.results = set([])
        self.data = {}

    def coverage_trace(self, frame, event, arg):
        module_name = frame.f_globals.get('__name__')
        if not module_name.startswith(self.module_name):
            return

        namespace = self.data.setdefault(module_name, {})
        func_name = frame.f_code.co_name
        if func_name in ['<listcomp>', '<dictcomp>']:
            return

        klass = get_class_from_frame(frame)
        if klass is not None:
            namespace = namespace.setdefault(klass.__name__, {})
        namespace.setdefault(func_name, {}) # TODO: put some args in this dict

    def _coverage_trace(self, frame, event, arg):
        module_name = frame.f_globals.get('__name__')
        if not module_name.startswith(self.module_name):
            return
        func_name = frame.f_code.co_name
        klass = get_class_from_frame(frame)
        if klass is not None:
            func_name = f'{klass.__name__}.{func_name}'
        path = f'{module_name}.{func_name}'
        if path not in self.results:
            print(path)
        self.results.add(path)


    def start(self):
        self.__enter__()

    def stop(self):
        self.__exit__(0,0,0)

    def __enter__(self):
        sys.settrace(self.coverage_trace)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        sys.settrace(None)

    def save(self, path=None):
        import json
        if path is None:
            folder = os.path.dirname(__file__)
            path = os.path.join(folder, 'coverage_output.json')
        with open(path, 'w') as fd:
            json.dump(trace.data, fd, indent=4)


if __name__ == '__main__':
    # ('b'=='a')
    with Trace('PythonEditor') as trace:
        from PythonEditor.ui.ide import IDE
        ide = IDE()
        ide.show()

        # from PythonEditor.ui.editor import Editor
        # editor = Editor()
        # editor.show()

    # trace = Trace('PythonEditor')
    trace.start()
    trace.stop()

    # sys.gettrace()
    trace.results
    import json
    folder = os.path.dirname(__file__)
    path = os.path.join(folder, 'coverage_output.json')

#&&

with open(path, 'w') as fd:
    json.dump(trace.data, fd, indent=4)
    # json.dump([trace.data, list(trace.results)], fd, indent=2)

#&&
# import ast
# ast.parse(

package_dir = os.path.dirname(os.path.dirname(__file__))
folder = os.path.join(package_dir, 'PythonEditor')
for root, dirs, files in os.walk(folder):
    base = root.replace(package_dir+os.sep, '').replace(os.sep, '.')
    for filename in files:
        route = '.'.join([base, filename.replace('.py', '')])
        try:
            namespace = trace.data[route]
            module = sys.modules[route]
            for _global in vars(module).keys():
                if _global not in namespace.keys():
                    print(_global)
            for _global in namespace:
                if _global in ['<lambda>', '<listcomp>', '<dictcomp>']:
                    continue
                item = getattr(module, _global)
                # module.globals(_global)
            # trace.data.keys()
        except KeyError:
            print(route)

# for trace.data