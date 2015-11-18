#!/usr/bin/env python

from pynzb import nzb_parser    # on Ubuntu: sudo apt-get install python-pynzb
from urllib2 import urlopen
import socket
import sys
import os

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


def getonelineMAKEFILE(s,command):
    if command!='':
        s.send(command+"\n")        
    for line in s.makefile('r'):
       myline = line.rstrip()
       return myline   

def getlinesuntildot(s,command):
    if command!='':
        s.send(command+"\r\n")
    End="\r\n.\r\n"
    total_data=[];data=''
    while True:
            data=s.recv(8192)
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




def getlinesuntildotMAKEFILE(s,command):
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
    result=getoneline(s,command)
    #print "result of BODY command:", result
    body = getlinesuntildot(s,'')
    return result,body
    
    
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
#print "LIST resultaat:", getlinesuntildot(s,'LIST')

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
        print 'Segment to handle: ' + segment.message_id
        result,body = getbody(s,segment.message_id)
	print "result:", result
	print "body (stukkie):", body[:100]
        counter += 1
        filename = resultdir + "/result---" + str(counter) + ".yenc"
        target = open(filename, 'w')
        target.write(body)
        target.close()
        
print getoneline(s,'QUIT')

        
        
