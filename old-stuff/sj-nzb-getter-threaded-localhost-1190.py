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

def connecttoserver(newsserver,port=119, username='', password='' ):
	print "port is", port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(4)
	 

	# connect to remote host
	try :
	    s.connect((newsserver,port))
	except :
	    print 'Unable to connect'
	    sys.exit()
	 
	print 'Connected to remote host'
	welcomemessage=getoneline(s,'')
	
	message=getoneline(s,'BODY <doesnot@exist>')
	# according to rfc3977:
	# 430 No such article # Good
	# 480 Authentication Required ... login required
	print "Result on random BODY command", message
        if message[:3] in ['430','412','423']:
		print "no login needed"
	else:
		print "login needed"
		'''
		authinfo user gekkie
		381 PASS required
		authinfo pass bekkie
		'''
	return s, welcomemessage

def getoneline(s,command):
    if command!='':
        s.send(command+"\r\n")
    End="\r\n"
    total_data=[];data=''
    while True:
            data=s.recv(1)          # only 1 character, to avoid reading from the next line
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
    return ''.join(total_data)

def getlinesuntildot(s,command):
    if command!='':
        s.send(command+"\r\n")
    End="\r\n.\r\n"
    total_data=[]
    data=''
    while True:
            data=s.recv(256*1024)	# we're reading a large chunk
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
    #return 'blablala'*100000
    #return ''.join(total_data)		# this is slow. Because of the join, or the data?
    return str(total_data)	# fast enough. But is this the same as the join does? 

def getbody(s,article):
    body=''
    command = "BODY <" + article + ">\n"
    result=getoneline(s,command)
    print "result of BODY command:", result
    # checking on the result...
    if result.find('2')==0:
		body = getlinesuntildot(s,'')
    return result,body




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
    s,welcomemsg=connecttoserver('127.0.0.1',1190)
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
num_threads = 12
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


