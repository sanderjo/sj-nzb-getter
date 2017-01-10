#import Queue
#import threading
#from Queue import Queue
import Queue
from threading import Thread
import time
import socket
from pynzb import nzb_parser    # on Ubuntu: sudo apt-get install python-pynzb
import sys
import os

# local module
from nntp_stuff import *

# Thread and Queue stuff: thank you, https://pymotw.com/2/Queue/

# The worker thread:
def downloadArticle(i, q):
    """This is the worker thread function.
    It processes items in the queue one after
    another.  These daemon threads go into an
    infinite loop, and only exit when
    the main thread ends.
    """
    print '%s: Thread started ...' % i
    print "Setting up stuff ..."
    s,welcomemsg=connecttoserver('newszilla6.xs4all.nl',119)
    print "Welcome message from newsserver:", welcomemsg

    print "Value is pleasecontinue is", pleasecontinue

    while pleasecontinue:		# keep reading and reading from the Queue
        print '%s: Thread working ...' % i
        myjob = q.get()
	group = myjob.group
	article = myjob.article
	filename = myjob.filename
        print '%s: Downloading:' % i, article

        command = "GROUP " + group
        print "GROUP:", getoneline(s,command)

        result,body = getbody(s,article)
	print "result:", result
	print "body (stukkie):", body[:100]
	print "filename is", filename
        target = open(filename, 'w')
        target.write(body)
        target.close()
        q.task_done()
    print '%s: Thread can stop ...' % i

class Job(object):
    def __init__(self, group, article, filename):
        self.group = group
        self.article = article
	self.filename = filename


### MAIN ###

if len(sys.argv) < 2:
    sys.exit('Usage: %s <nzb-filename>' % sys.argv[0])

nzbfilename = sys.argv[1]
my_nzb = open(nzbfilename).read()
files = nzb_parser.parse(my_nzb)


articlequeue = Queue.Queue()    # queue used for feeding articles to threads

pleasecontinue = True


# Set up threads:
num_threads = 4
for i in range(num_threads):
    worker = Thread(target=downloadArticle, args=(i, articlequeue,))
    worker.setDaemon(True)
    worker.start()

counter=100000	# for the filenames
import time
timestamp = int(time.time())
resultdir = "result---" + str(timestamp)
os.mkdir(resultdir)


# Fill queue:
for nzb_file in files:
    print nzb_file.subject
    group = nzb_file.groups[0]

    #command = "GROUP " + group
    #print "GROUP:", getoneline(s,command)
    for segment in nzb_file.segments:
	article = segment.message_id
        print 'Segment to handle: ' + article
        counter += 1
        filename = resultdir + "/result---" + str(counter) + ".yenc"
	articlequeue.put(Job(group,article,filename))

print "Queue filled", articlequeue

# Now wait for the queue to be empty, indicating that we have
# processed all of the downloads.
print '*** Main thread waiting'
articlequeue.join()
print '*** Done'

pleasecontinue = False

time.sleep(10)
print "Exit"


