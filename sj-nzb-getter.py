#!/usr/bin/env python

from pynzb import nzb_parser    # on Ubuntu: sudo apt-get install python-pynzb
from urllib2 import urlopen
import socket
import sys
import os

def getoneline(s,command):
    if command!='':
        s.send(command+"\n")        
    for line in s.makefile('r'):
       myline = line.rstrip()
       return myline   

def getlinesuntildot(s,command):
    if command!='':
        #print "INCOMING command:", command
        s.send(command+"\n") 
    lines = s.makefile('r')
    linecounter=0
    total=""
    for line in lines:
        linecounter += 1
        myline = line.rstrip()
        #print myline
        if linecounter==1:
            #print "Response:", myline
            if myline.find('4')==0 or myline.find('5')==0:
                # some error message
                break
        if myline.find('.')==0:
            # the dot that indicates the end of the block, so ... :
            break
        total = total + myline + "\n"
    return total

def getbody(s,article):
    command = "BODY <" + article + ">\n"
    result=getlinesuntildot(s,command)   
    firstline = result.split("\n")[0]
    body = "\n".join(result.split("\n")[1:]) + "\n"
    return firstline,body
    
    
### MAIN ###

if len(sys.argv) < 2:
    sys.exit('Usage: %s <nzb-filename>' % sys.argv[0])

nzbfilename = sys.argv[1]
my_nzb = open(nzbfilename).read()
files = nzb_parser.parse(my_nzb)

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.settimeout(2)
 
# connect to remote host
try :
    s.connect(('newszilla6.xs4all.nl',119))
except :
    print 'Unable to connect'
    sys.exit()
 
print 'Connected to remote host'

# Get Welcome message:
print "Welkom bericht:", getoneline(s,'')

#print "DATE resultaat:", getoneline(s,'DATE')
#print "HELP resultaat:", getlinesuntildot(s,'HELP')
#print "BLABLA resultaat:", getoneline(s,'BLABLA')

# Print out each file's subject and the first two segment message ids
counter=100000
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
        print 'Segment to handle:' + segment.message_id
        result,body = getbody(s,segment.message_id)
        counter += 1
        filename = resultdir + "/result---" + str(counter) + ".yenc"
        target = open(filename, 'w')
        target.write(body)
        target.close()
        
print getoneline(s,'QUIT')

        
        
