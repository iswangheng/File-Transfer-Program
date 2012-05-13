'''
Created on 29 Sep 2010

@author: swarm
'''

import wx
import sys
import time
import os 
from filetrans import *
import MyThread

data =""
host = ""
port = 51234
BUFSIZE = 1024 
fileTrans = FileTrans(("",51234))

userdata = [('oneone', 'swarm')]

class SwarmTrans(wx.Frame):
    def __init__(self, parent, id, title):
        
        wx.Frame.__init__(self, parent, id, title,size=(430,280))

        panel = wx.Panel(self,-1)
 
        self.font = wx.Font(pointSize = 10,family = wx.FONTFAMILY_DEFAULT, style = wx.FONTSTYLE_NORMAL, weight = wx.FONTWEIGHT_NORMAL, underline = False, face = wx.EmptyString,encoding = wx.FONTENCODING_DEFAULT)

        self.SetMinSize(wx.Size(300,300))
        self.SetMaxSize(wx.Size(500,500))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        bkgsizer = wx.GridBagSizer(4,4)
        
        #below is the list which shows who is online!
        self.list = wx.ListCtrl(panel, -1,
                style=wx.LC_REPORT)
        self.list.InsertColumn(0,
                'User', wx.LIST_FORMAT_LEFT, width = -1)
        self.list.InsertColumn(1, 'Host', wx.LIST_FORMAT_LEFT,width = -1)
        for i in range(2):
            self.list.SetColumnWidth(i, 100)
        for i in userdata:
            index = self.list.InsertStringItem(sys.maxint, i[0])
            self.list.SetStringItem(index, 1, i[1])
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.list.SetFont(self.font)
            
        #below is the static text "Member:" which shows the number of members online
        self.textmember = wx.StaticText(panel,-1,"Members: ",style = wx.ALIGN_LEFT)
        self.textnum = wx.StaticText(panel,-1,"1 ",style = wx.ALIGN_CENTER)
        self.textmember.SetFont(self.font)
        self.textnum.SetFont(self.font)

        #below is the refresh button
        self.buttonrefresh = wx.Button(panel,-1, label="Refresh", size=(80, 30))
        self.buttonrefresh.SetToolTipString("Refresh to see if someone new here..") 
        self.buttonrefresh.SetFont(self.font)
        self.Bind(wx.EVT_BUTTON, self.OnClick,self.buttonrefresh)
        
        #below is the static text A,B,D,E:
        self.textA = wx.StaticText(panel,-1,"You can...",style = wx.ALIGN_CENTER)
        self.textB = wx.StaticText(panel,-1,"Transfer files safely and soundly",style = wx.ALIGN_CENTER)
        self.textD = wx.StaticText(panel,-1,"",style = wx.ALIGN_CENTER)
        self.textE = wx.StaticText(panel,-1,"",style = wx.ALIGN_CENTER)
        self.textF = wx.StaticText(panel,-1,"with DiffieHellman key exchange and AES algorithm",style = wx.ALIGN_CENTER)
        self.textA.SetFont(self.font)
        self.textB.SetFont(self.font)
        self.textD.SetFont(self.font)
        self.textE.SetFont(self.font)
        self.textF.SetFont(self.font)
         
        #below is the send button
        self.buttonsend = wx.Button(panel, -1, label = "Send", size =(100,30))
        self.buttonsend.SetToolTipString("Click send to transfer files!")
        self.buttonsend.SetFont(self.font)
        self.Bind(wx.EVT_BUTTON, self.OnClick,self.buttonsend)
        
        #below is the pause button
        self.buttonpause = wx.Button(panel, -1, label = "Pause", size = (100,30))
        self.buttonpause.SetToolTipString("Click here to pause the transfer")
        self.buttonpause.SetFont(self.font)
        self.Bind(wx.EVT_BUTTON, self.OnClick,self.buttonpause)
     
        bkgsizer.Add(self.list,(0,0),(4,4),flag = wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND,border = 4)
        bkgsizer.Add(self.textmember,(0,4),(1,1),flag = wx.TOP|wx.RIGHT|wx.LEFT|wx.EXPAND, border = 10)
        bkgsizer.Add(self.textnum,(1,4),(1,1),wx.TOP|wx.RIGHT|wx.LEFT|wx.EXPAND, border = 10)
        bkgsizer.Add(self.buttonrefresh,(2,4),(1,1),border = 9)
        bkgsizer.Add(self.textA,(4,0),(1,1),border = 11)
        bkgsizer.Add(self.textB,(5,0),(1,2),border = 11)
        bkgsizer.Add(self.textD,(5,2),(1,1),border = 11)
        bkgsizer.Add(self.textE,(5,3),(1,1),border = 11)
        bkgsizer.Add(self.textF,(6,0),(1,5),border = 11)
        bkgsizer.Add(self.buttonsend,(7,1),(1,1),border = 5)
        bkgsizer.Add(self.buttonpause,(7,3),(1,1),border = 5)


        bkgsizer.AddGrowableRow(3)
        bkgsizer.AddGrowableRow(4)
        bkgsizer.AddGrowableRow(5)
        bkgsizer.AddGrowableRow(6)
        for j in range(6):
            bkgsizer.AddGrowableCol(j)

        panel.SetSizerAndFit(bkgsizer)
         
        
        self.Centre()
        self.Show(True)
        panel.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        

        
    def OnContextMenu(self, event):
        #below is the popup menu
        self.popupID = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnPopup, id = self.popupID)
        menu = wx.Menu()
        menu.Append(self.popupID,"About")
        self.PopupMenu(menu)
        menu.Destroy()
    
    def OnPopup(self,event):
        '''Popup an about dialog.
        '''
        info = wx.AboutDialogInfo()
        info.Name = 'Swarm\'s File Transfer'
        info.Version = 'V1.0'
        info.Copyright = '(C) 2010 Swarm'
        info.Description = '''\nA Simple Encrypted File Transfer \n
Written in Python.
GUI Powered by wxPython.'''
        info.Developers = ['swarm<cnjswangheng66@gmail.com>']

        wx.AboutBox(info) 
            
    def UpdateList(self,userlist):
        self.list.DeleteAllItems()
        userdata = []
        usernums = 0
        for i in userlist:
            userdata.append((i[0],i[1]))
            usernums += 1
        for i in userdata:
            index = self.list.InsertStringItem(sys.maxint, i[0])
            self.list.SetStringItem(index, 1, i[1])
        self.textnum.SetLabel(str(usernums))
            
    def OnDoubleClick(self,event):
        '''open a file to transfer
        '''
        dirname = ''
        ctrl = event.GetEventObject()
        idx = ctrl.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
        if idx != -1:
            itemusername = ctrl.GetItem(idx, 0).GetText()
            itemhostname = ctrl.GetItem(idx, 1).GetText()
            opendlg = wx.FileDialog(self,'Choose a file to transfer',dirname,'','*',wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)        
            if opendlg.ShowModal() == wx.ID_OK: 
                filename = opendlg.GetPath() 
                for i in userlist: 
                    if (itemusername == i[0]) and (itemhostname == i[1]):
                        addr = i[2]
                        port = i[3] 
                        fileTrans.sendfile(filename, (addr, port),fileTrans.username)
                        break
            opendlg.Destroy()    
            
    def OnClick(self,event):
        if event.GetId() == self.buttonpause.GetId():         
            if self.buttonpause.GetLabel() == "Pause":  
                self.buttonpause.SetLabel("Continue")
            else:
                self.timer.Start(100)
                self.buttonpause.SetLabel("Pause")
        elif event.GetId() == self.buttonrefresh.GetId():
            fileTrans.broadcast()
            userlist = fileTrans.getUserlist()
            self.UpdateList(userlist)
        elif event.GetId() == self.buttonsend.GetId():
            idx = self.list.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
            if idx != -1:
                itemusername = self.list.GetItem(idx, 0).GetText()
                itemhostname = self.list.GetItem(idx, 1).GetText()
                opendlg = wx.FileDialog(self,'Choose a file to transfer',"",'','*',wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)        
                if opendlg.ShowModal() == wx.ID_OK: 
                    filename = opendlg.GetPath()                   
                    userlist = fileTrans.getUserlist()
                    for i in userlist: 
                        if (itemusername == i[0]) and (itemhostname == i[1]):
                            addr = i[2]
                            port = i[3] 
                            fileTrans.sendfile(filename, (addr, port),fileTrans.username)
                            break
                opendlg.Destroy()    
            
    def OnClose(self,event):
        fileTrans.CloseSocket()
        self.Destroy() 

def main():
    app = wx.App(redirect = False)
    swarm = SwarmTrans(None,-1,'Swarm\'s File Transfer')
    fileTrans.broadcast()
    fileTrans.eventLoop()
    userlist = fileTrans.getUserlist()
    swarm.UpdateList(userlist)
    app.MainLoop()     
    
if __name__ == '__main__':
    main()
