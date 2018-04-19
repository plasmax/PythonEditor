# from queue import Queue
# import os

# q = Queue()

from PythonEditor.ui import output
reload(output)
out = output.Output()
out.show()

print('hi')

folder = os.path.dirname(__file__)
for root, dirs, files in os.walk(folder):
    for file in files:
        path = os.path.join(root, file)

        if not path.endswith('.py'):
            continue

        with open(path, 'rt') as f:
            data = f.read().splitlines()

        for row in data:
            q.put(row)

# while not q.empty():
#     print(q.get())
#     print(q.qsize())

#for x in range(1000):
    #if not q.empty():
        #print(q.get())



