import multiprocessing

def worker():
    """worker function"""
    print 'Worker'
    bla = 0 
    for i in xrange(10000000):
	bla = bla + i*3*3
	#print bla
    print "Done", bla
    return

if __name__ == '__main__':
    jobs = []
    for i in range(10):
        p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()

