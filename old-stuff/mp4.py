import multiprocessing
import time
import random
from pynzb import nzb_parser    # on Ubuntu: sudo apt-get install python-pynzb


# local module
from nntp_stuff import *


def worker(num, newsserver, q):
    """thread worker function"""

    print '%s: Thread started ...' % i
    print "Setting up stuff ..."
    s,welcomemsg=connecttoserver(newsserver.newsserver,newsserver.port, newsserver.username, newsserver.password)
    if s: 
    	print "Welcome message from newsserver:", welcomemsg
    else:
	print "no succesful connection"
	return

    print 'Worker:', num
    while True:
	myjob = q.get()
	if myjob == None:
		break
	print 'Worker:', num, myjob.group, myjob.article, myjob.filename
	group = myjob.group
	article = myjob.article
	filename = myjob.filename
        print '%s: Downloading:' % i, article

        command = "GROUP " + group
        print "GROUP:", getoneline(s,command)

        result,body = getbody(s,article)
	print "result:", result
	print "body (stukkie):", body[:100]

	# write the article to the filename
	print "filename is", filename
        target = open(filename, 'w')
        target.write(body)
        target.close()

    return

class Job(object):
    def __init__(self, group, article, filename):
        self.group = group
        self.article = article
	self.filename = filename

class Newsserver(object):
    def __init__(self, newsserver, port, username, password):
	self.newsserver = newsserver
	self.port = port
	self.username = username
	self.password = password


########### MAIN #############

if __name__ == '__main__':


	try:
		server = sys.argv[1].split(':')[0]
		try:
			port = int(sys.argv[1].split(':')[1])
		except:
			port = 119
		print "port is", port
		connections = int(sys.argv[2])
		username = sys.argv[3]
		password = sys.argv[4]
		nzbfilename = sys.argv[5]
	except:
		print "Usage: python", sys.argv[0],  "newsserver number-of-connections username password nzb-filename"

		print "Example usage: python", sys.argv[0],  "newsreader.eweka.nl 8 JohnDoe SeCrEt mynzb.nzb"
		print "Example usage: python", sys.argv[0],  "newszilla6.xs4all.nl 4 none none mynzb.nzb"
		print "Example usage: python", sys.argv[0],  "localhost:1190 10 bla bla mynzb.nzb "
		sys.exit(0)
		pass

	#mynewsserver = Newsserver("newszilla6.xs4all.nl", 119, "bla", "bla")
	mynewsserver = Newsserver(server, port, username, password)

	# prepare directory:
	resultdir = "result---" + str(int(time.time()))
	os.mkdir(resultdir)	# create directory to store the retrieved files
	counter=100000	# for the filenames

	# Fill queue with articles to be fetched:
	my_nzb = open(nzbfilename).read()
	files = nzb_parser.parse(my_nzb)
	q = multiprocessing.Queue()
	for nzb_file in files:
	    print nzb_file.subject
	    group = nzb_file.groups[0]

	    for segment in nzb_file.segments:
		article = segment.message_id
		print 'Segment to handle: ' + article
		counter += 1
		filename = resultdir + "/result---" + str(counter) + ".yenc"
		q.put(Job(group,article,filename))



	# Start the processes:
	jobs = [] 
	numberofprocesses = connections	# max concurrent processes (=NNTP sessions) to newsserver
	for i in range(numberofprocesses):
		p = multiprocessing.Process(target=worker, args=(i, mynewsserver, q))
		jobs.append(p)
		p.start()

	# Signal processes to stop
	for i in range(100):
		q.put(None)

	print "Done!!!"



