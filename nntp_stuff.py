import time
import socket
import sys
import os

debug = True

def connecttoserver(newsserver,port=119, username='', password='' ):
	# this function connects to server
	# returns the socket (to be reused), and the welcome message

	if debug:
		print "newsserver is", newsserver 
		print "port is", port

	# connect to newsserver
	# First IPv4:
	try :
	    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    s.settimeout(4)
	    s.connect((newsserver,port))
	except :
	    if debug:
		print 'Ouch .... Unable to connect via IPv4'
	    # ... now let's try IPv6:
	    try :
		    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		    s.settimeout(4)
		    s.connect((newsserver,port))
	    except :
		    print 'Ouch .... Unable to connect via IPv6'
		    return None, None
	 
	print 'Connected to remote host'
	welcomemessage=getoneline(s,'')
	
	message=getoneline(s,'BODY doesnot@exist')
	if debug:
		print "message to BODY command is", message
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
		command = "AUTHINFO USER " + username
		message=getoneline(s,command)
		if debug:
			print "after username is", message

		command = "AUTHINFO PASS " + password
		message=getoneline(s,command)
		if debug:
			print "after password is", message
			if message[0] == '2':
				# 281 OK (No Posting)
				print "Login OK"
			if message[0] == '5':
				# 502 Authentication Failed
				print "Login failed"
				s = None

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


if __name__ == '__main__':
	# just something
	#print connecttoserver('newszilla.xs4all.nl')

	try:
		server = sys.argv[1].split(':')[0]
		try:
			port = int(sys.argv[1].split(':')[1])
		except:
			port = 119
		print "port is", port
		username = sys.argv[2]
		password = sys.argv[3]
		mysocket, result = connecttoserver(server, port, username, password)
	except:
		print "Example usage: python nntp_stuff.py  newsreader.eweka.nl 66666 SeCrEt  "
		print "Example usage: python nntp_stuff.py  newszilla6.xs4all.nl none none"
		print "Example usage: python nntp_stuff.py  newsreader.eweka.nl 66666 SeCrEt  alt.binaries.mom 'part1of61.XPzUSVyOh2Nkek2ongtT@camelsystem-powerpost.local' "
		print "Example usage: python nntp_stuff.py localhost:1190 bla bla alt.binaries.test   '400M-binnie.bin?10=4500000:500000' "
		sys.exit(0)
		pass


	try:
		group = sys.argv[4]
		article = sys.argv[5]
		command = "GROUP " + group
		if debug:
			print "group command", command
		message=getoneline(mysocket,command)
		if debug:
			print "after GROUP is", message

		result, body = getbody(mysocket, article)
		print result
		print body[:200]
		print "<.......>"
		print body[-200:]
	except:
		pass




