import time
import os 
import sys
import chilkat
from MyThread import  *

data =""

BUFSIZE = 1024 

class FileTrans(object):
    def __init__(self,(addr,port)):
        count = 0
        self.username = os.environ['USERNAME']
        self.hostname = os.environ['COMPUTERNAME']
        self.udpsocket = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
        self.udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.udpsocket.bind((host,port))

    def broadcast(self):
        data = self.username
        data = data + ";"+self.hostname+";"
        data += 'hi'
        self.udpsocket.sendto(data,('255.255.255.255', port))
    
    def getUserlist(self):
        return userlist
    
    def sendfile(self,filename,(addr,port),username):
        SendFilesThread(filename,(addr,port),username).start()
        
    def eventLoop(self):
        self.udpThread =  UDPThread(self)
        self.udpThread.start()
        self.tcpThread =  TCPThread(self)
        self.tcpThread.start() 
    
    def CloseSocket(self):
        self.udpsocket.close()
        os._exit(0)