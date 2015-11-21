# System modules
from Queue import Queue
from threading import Thread
import time

# Local modules
import feedparser

# Set up some global variables
num_fetch_threads = 2
enclosure_queue = Queue()

# A real app wouldn't use hard-coded data...
feed_urls = [ 'http://www.castsampler.com/cast/feed/rss/guest',
		'http://haaa',
		'http://dddd',
		'http://xxdd',
		'http://dadsf',
		'http://ddadsfasdfdd',
             ]


class Job(object):
    def __init__(self, group, article, filename):
        self.group = group
        self.article = article
	self.filename = filename


def downloadEnclosures(i, q):
    """This is the worker thread function.
    It processes items in the queue one after
    another.  These daemon threads go into an
    infinite loop, and only exit when
    the main thread ends.
    """
    while True:
        print '%s: Looking for the next url' % i
        somejob = q.get()
        print '%s: Downloading:' % i, somejob.group
        # instead of really downloading the URL,
        # we just pretend and sleep
        time.sleep(i + 2)
        q.task_done()


# Set up some threads to fetch the enclosures
for i in range(num_fetch_threads):
    worker = Thread(target=downloadEnclosures, args=(i, enclosure_queue,))
    worker.setDaemon(True)
    worker.start()

# Download the feed(s) and put the enclosure URLs into
# the queue.
bakkie = {}
for url in feed_urls:
	#bakkie['url']=url
	#bakkie['bron']='weet ik niet meer'
	enclosure_queue.put(Job(url,'weet ik niet meer'))
        
# Now wait for the queue to be empty, indicating that we have
# processed all of the downloads.
print '*** Main thread waiting'
enclosure_queue.join()
print '*** Done'

