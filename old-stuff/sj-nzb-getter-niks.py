#!/usr/bin/env python

from pynzb import nzb_parser    # on Ubuntu: sudo apt-get install python-pynzb
from urllib2 import urlopen
import socket
import sys
import os

def connecttoserver(newsserver,port=119, username='', password='' ):
	s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
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
            data=s.recv(8192)	# we're reading a large chunk
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


def getbody(s,article):
    body=''
    command = "BODY <" + article + ">\n"
    result=getoneline(s,command)
    print "result of BODY command:", result
    # checking on the result...
    if result.find('2')==0:
		body = getlinesuntildot(s,'')
    return result,body


    
    
### MAIN ###

if len(sys.argv) < 2:
    sys.exit('Usage: %s <nzb-filename>' % sys.argv[0])

nzbfilename = sys.argv[1]
my_nzb = open(nzbfilename).read()
files = nzb_parser.parse(my_nzb)

s,welcomemsg=connecttoserver('newszilla6.xs4all.nl',119)
# show Welcome message:
print "Welkom bericht:", welcomemsg

#print "DATE resultaat:", getoneline(s,'DATE')
#print "HELP resultaat:", getlinesuntildot(s,'HELP')
#print "LIST resultaat:", getlinesuntildot(s,'LIST')

#print "BLABLA resultaat:", getoneline(s,'BLABLA')

# Print out each file's subject and the first two segment message ids
counter=100000	# for the filenames
import time
timestamp = int(time.time())
resultdir = "result---" + str(timestamp)
os.mkdir(resultdir)

for nzb_file in files:
    print nzb_file.subject
    group = nzb_file.groups[0]
    command = "GROUP " + group
    print "GROUP:", getoneline(s,command)
    for segment in nzb_file.segments:
        print 'Segment to handle: ' + segment.message_id
        result,body = getbody(s,segment.message_id)
	#print "result:", result
	#print "body (stukkie):", body[:100]
        counter += 1
        filename = resultdir + "/result---" + str(counter) + ".yenc"
        target = open(filename, 'w')
        target.write(body)
        target.close()
        
print getoneline(s,'QUIT')

        
        
