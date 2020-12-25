import _thread as thread, time

stdoutmutex = thread.allocate_lock()
numthreads = 5
exitmutexes = [thread.allocate_lock() for i in range(numthreads)]

def counter(myId, count, mutex):
    for i in range(count):
        time.sleep( 1/ (myId+1))
        mutex.acquire()
        print("[%s] ==> %s" % (myId, i))
        mutex.release()
    exitmutexes[myId].acquire()

for i in range(5):
    thread.start_new_thread(counter, (i, 5, stdoutmutex))

while not all(mutex.locked for mutex in exitmutexes): time.sleep(0.25)

print("Main thread exiting")