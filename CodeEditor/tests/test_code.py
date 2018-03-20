import jedi
source = '''
import datetime
datetime.da
import os
os.wa
'''

script = jedi.Script(source, 3, len('datetime.da'), 'example.py')
print(script)

completions = script.completions()
print(completions)

print(completions[0].complete)

print(completions[0].name)

script = jedi.Script(source, 5, len('os.wa'), 'example.py')

print(len(source))