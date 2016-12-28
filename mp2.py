import multiprocessing
import time

def worker(num, q):
    """thread worker function"""
    print 'Worker:', num
    while True:
	item = q.get()
	if item == None:
		break
	print 'Worker:', num, item
	time.sleep(0.3)
    return

if __name__ == '__main__':

    jobs = []

    print "Put stuff into queue"
    q = multiprocessing.Queue()
    for item in range(100):
	q.put(item)

    # Start the processes:
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,q))
        jobs.append(p)
        p.start()

    # Signal processes to stop
    for i in range(5):
	q.put(None)



