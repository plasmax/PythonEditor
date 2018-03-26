""" For testing within nuke """
PACKAGE_PATH = '/net/homes/mlast/.nuke/python/max/tests/CodeEditor'
TEST_FILE = os.path.join( PACKAGE_PATH, 'tests/test_code.py')

with open( TEST_FILE, 'r' ) as f:
    TEST_CODE = f.read()

sys.path.append(PACKAGE_PATH)

for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]

import PythonEditor
reload(PythonEditor)
ide = PythonEditor.ide.IDE()
ide.show()
ide.editor.setPlainText(TEST_CODE)

import nukescripts
nukescripts.registerWidgetAsPanel('__import__("PythonEditor").ide.IDE', 
                                  'Python Editor', 'i.d.e')
