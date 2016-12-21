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
	time.sleep(1)
    return

if __name__ == '__main__':
    jobs = []
    q = multiprocessing.Queue()
    for item in range(100):
	q.put(item)

    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,q))
        jobs.append(p)
        p.start()

    for i in range(5):
	q.put(None)



