import threading 
import socket
import time
import os
import sys 
import wx
import chilkat

host = ""
port = 51234
MAX_UDPBUF = 16384
MAX_TCPBUF = 65536/2
BUFSIZE = 1024
FILEINFO_SIZE = 1024
userlist = []
global event 
event = threading.Event()
countval = 1

class UDPThread(threading.Thread):
    def __init__(self, filetrans):
        threading.Thread.__init__(self)
        self.filetrans = filetrans
        
    def run(self):
        while True:
            recvdatalist = []
            data, (addr,port) = self.filetrans.udpsocket.recvfrom(MAX_UDPBUF)
            recvdatalist = data.split(";")
            msg = recvdatalist.pop()
            recvdatalist.append(addr)
            recvdatalist.append(port)
            recvdatalist.append(msg)
            if(msg == 'hi'):
                if recvdatalist not in userlist:
                    userlist.append(recvdatalist)

class TCPThread(threading.Thread):
    def __init__(self,filetrans):
        threading.Thread.__init__(self)
        self.filetrans = filetrans
    
    def run(self):
        while True:                    
            self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpsocket.bind((host,port))
            self.tcpsocket.listen(True)     
            sock, addr = self.tcpsocket.accept() 
            fhead = sock.recv(FILEINFO_SIZE)
            fheadlist = fhead.split(";")
            filename = fheadlist[0]
            filesize = fheadlist[1]  
            sendusername = fheadlist[2] 
            
            recvmsg = "Do you want to save "
            filenamelist = filename.split('\\') 
            tosavefilename = str(filenamelist.pop())
            recvmsg += "\""+tosavefilename +"\""+" from "+str(sendusername)+"?"
            tosavefilenamelist = tosavefilename.split('.')
            filesuffix = "*."
            filesuffixname = tosavefilenamelist.pop() 
            filesuffix += filesuffixname 
            msgdlg = wx.MessageDialog(None, recvmsg,'Receive file?', wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
            msgdlgvar = msgdlg.ShowModal()   
         
            
            dhAlice = chilkat.CkDh()
            eBob = 0x01
            p = ""
            g = 1
            
         
            if msgdlgvar == wx.ID_YES:                
                sock.sendall("YES")
                while True:
                    response = sock.recv(1024)
                    if response == 'gotYES':
                        sock.sendall("keyexchange")
                    elif response == 'sendkey':
                        pgdata = sock.recv(1024)
                        if pgdata:
                            pglist = pgdata.split(";")
                            p = pglist[0]
                            g = int(pglist[1])
                            success = dhAlice.SetPG(p,g) 
                            sock.sendall("sendeBob") 
                    elif response == 'willsendeBob':
                        eBob = sock.recv(1024)
                        sock.sendall('willsendeAlice')
                        eAlice = dhAlice.createE(256)
                        sock.send(eAlice)
                    elif response == 'goteAlice':
                        sock.send('senddata')
                    elif response == "willsendata":
                        break
                
                kAlice = dhAlice.findK(eBob)
#                print "Alice's shared secret (should be equal to Bob's)",kAlice
                time.sleep(1)      
                savedlg = wx.FileDialog(None, 'Save file to...', '', '', filesuffix, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if savedlg.ShowModal() == wx.ID_OK:
                    filenamepath = savedlg.GetPath()

                    crypt = chilkat.CkCrypt2()
                    success = crypt.UnlockComponent("Anything for 30-day trial.")
                    if (success != True):
                        print crypt.lastErrorText()
                        sys.exit()
                    crypt.put_EncodingMode("hex")
                    crypt.put_HashAlgorithm("md5")
                    
                    sessionKey = crypt.hashStringENC(kAlice)
                    
    #                print "128-bit Session Key:"
    #                print sessionKey
                    #  Encrypt something...
                    crypt.put_CryptAlgorithm("aes")
                    crypt.put_KeyLength(128)
                    crypt.put_CipherMode("cbc")
                    
                    #  Use an IV that is the MD5 hash of the session key...
                    
                    iv = crypt.hashStringENC(sessionKey)
                    
                    #  AES uses a 16-byte IV:
    #                print "Initialization Vector:"
    #                print iv
                    
                    crypt.SetEncodedKey(sessionKey,"hex")
                    crypt.SetEncodedIV(iv,"hex")
                    crypt.put_EncodingMode("base64")
     
                    fp = open(filenamepath,'wb') 
                    while True: 
                        filedata = sock.recv(1024) 
                        crypt.decryptStringENC(filedata)                                       
                        if not filedata:
                            break   
                        fp.write(filedata)  
                    fp.flush()                           
                    fp.close() 
                    sock.close() 
                    self.tcpsocket.close()
                    finishmsg = "\""+tosavefilename+"\""+" is saved in "+filenamepath
                    finishdlg = wx.MessageDialog(None, finishmsg, 'Done!',  wx.OK | wx.ICON_INFORMATION )
                    finishdlg.ShowModal()
                else:         
                    sock.close() 
                    self.tcpsocket.close()
            else:
                sock.sendall("NO")
                sock.close() 
                self.tcpsocket.close()


class SendFilesThread(threading.Thread):
    def __init__(self,filename,(addr,port),username): 
        threading.Thread.__init__(self)
        self.filename = filename
        self.addr = addr
        self.port = port
        self.username = username  
    
    def run(self):
        sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sendsock.connect((self.addr,self.port)) 
        filesize = os.stat(self.filename).st_size 
        fhead = ""+str(self.filename)+";"+str(filesize)+";"+str(self.username)
        sendsock.send(fhead)   
        
        ##Now is the key exchange part!!
        dhBob = chilkat.CkDh()     
        eAlice = 0x10    
        eBob = 0x10
        ##  Unlock the component once at program startup...
        success = dhBob.UnlockComponent("Anything for 30-day trial")
        dhBob.UseKnownPrime(2)
                        
        response = sendsock.recv(1024) 
        if response == 'YES':      
            sendsock.send("gotYES")           
            while True:
                response = sendsock.recv(1024)
                if response == "keyexchange":
                    sendsock.sendall("sendkey")
                    #  Bob will now send P and G to Alice.
                    p = dhBob.p()
                    g = dhBob.get_G()
                    pgdata = p+";"+str(g)
                    sendsock.send(pgdata) 
                elif response == 'sendeBob':
                    sendsock.sendall("willsendeBob")
                    eBob = dhBob.createE(256)
                    sendsock.send(eBob) 
                elif response == 'willsendeAlice': 
                    eAlice =  sendsock.recv(1024)
                    sendsock.sendall('goteAlice')
                elif response == 'senddata':
                    sendsock.sendall("willsendata")
                    break      
                
                
            kBob = dhBob.findK(eAlice) 
#            print "Bob's shared secret:"
#            print kBob    
            
            crypt = chilkat.CkCrypt2()
            success = crypt.UnlockComponent("Anything for 30-day trial.")
            if (success != True):
                print crypt.lastErrorText()
                sys.exit()
            crypt.put_EncodingMode("hex")
            crypt.put_HashAlgorithm("md5")
            
            sessionKey = crypt.hashStringENC(kBob)
            
#            print "128-bit Session Key:"
#            print sessionKey
            #  Encrypt something...
            crypt.put_CryptAlgorithm("aes")
            crypt.put_KeyLength(128)
            crypt.put_CipherMode("cbc")
            
            #  Use an IV that is the MD5 hash of the session key...
            
            iv = crypt.hashStringENC(sessionKey)
            
            #  AES uses a 16-byte IV:
#            print "Initialization Vector:"
#            print iv
            
            crypt.SetEncodedKey(sessionKey,"hex")
            crypt.SetEncodedIV(iv,"hex")
            crypt.put_EncodingMode("base64")
            
            fp = open(self.filename,'rb')
            tempcount = 0        
            while True: 
                event.clear()            
                filedata = fp.read(BUFSIZE) 
                tempcount += len(filedata) 
                countval = (tempcount * 100)/filesize  
                if not filedata: break  
                crypt.encryptStringENC(filedata)
                sendsock.send(filedata)  
                event.set()
            fp.close()     
            self.start = SendTipThread().start()  
        elif response == 'NO':
            pass
        else:
            pass
        sendsock.close()  
        
class SendTipThread(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self) 
        
    def run(self): 
        sendfinishmsg = "File has been sent over completely"
        finishdlg = wx.MessageDialog(None, sendfinishmsg, 'Done!',  wx.OK | wx.ICON_INFORMATION )
        finishdlg.ShowModal()
     
    
    
