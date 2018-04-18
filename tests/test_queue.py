from queue import Queue

q = Queue()

for x in range(100):
    q.put('bank')


while not q.empty():
    print(q.get())
    print(q.qsize())

#for x in range(1000):
    #if not q.empty():
        #print(q.get())


