'''
Created on Jan 7, 2013

@author: Davis Mariotti
'''
from Tkinter import *
import Tkinter, Queue, thread, os, time
from time import *
from thread import *
from PodSixNet.Connection import connection, ConnectionListener
class Console(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.queue = Queue.Queue()
        self.updateMe()
    def write(self, line):
        self.queue.put(line)
    def clear(self):
        self.queue.put(None)
    def updateMe(self):
        try:
            while 1:
                line = self.queue.get_nowait()
                if line != None:
                    self.insert(END, str(line)+"\n")
                self.see(END)
                self.update_idletasks()
        except Queue.Empty:
            pass
        self.after(100, self.updateMe)
    
def pipeToWidget(input, widget):
    widget.clear()
    if not input:
        return
    widget.write(input)
        
def toTextBox(widget, input):
    pipeToWidget(input, widget)

class Client(ConnectionListener):
    global players
    global widget
    players = []
    def __init__(self, host, port, nick):
        self.Connect((host, port))
        
        if nick == "":
            nick = "Anonymous"
        connection.Send({"action": "nickname", "nickname": nick})
        # launch our threaded input loop
        #t = start_new_thread(self.InputLoop, ())
    
    def Loop(self):
        connection.Pump()
        self.Pump()
    
    
    def send(self,data):
        connection.Send({"action": "message", "message": data})
    #######################################
    ### Network event/message callbacks ###
    #######################################
    
    def Network_players(self, data):
        global players
        #Recieved list of players.
        players = data['players']
    
    def Network_message(self, data):
        #Got a message.
        print data['from'] + ": " + data['message']
        thread.start_new(toTextBox, (widget, data['from']+": "+data['message']))
    def Network_serverMessage(self, data):
        msg = data['message']
        print "Server:",msg
    def Network_PMrecieve(self, data):
        msg = data['message']
        of = data['from']
        print "PM from " + of + ": " + msg
    def Network_PMsuccess(self, data):
        success = data['success']
        if success == True:
            print "PM successfully sent!"
        else:
            print "Error, recipient may not be online."
        
    # built in stuff
    def Network_connected(self, data):
        print "You are now connected to the server"
    
    def Network_error(self, data):
        print 'error:', data['error'][1]
        connection.Close()
    
    def Network_disconnected(self, data):
        print 'Server disconnected'
        exit()


def sendStuff():
    global widget
    global entry
    global c
    c.send(entry.get())
    entry.delete(0,END)
    widget.yview(END)
def sendStuffEvent(event):
    sendStuff()
global host, port, nickname    
host = "127.0.0.1"
port = 12345
nickname = ""
def showPref():
    global host, port, nickname
    def save():
        global host, port, nickname
        host = hostEntry.get()
        port = int(portEntry.get())
        nickname = nickEntry.get()
        print nickname
    win2 = Tk()
    labelHost = Label(win2,text="Host: ")
    hostEntry = Entry(win2)
    labelHost.pack()
    hostEntry.pack()
    hostEntry.insert(0, "127.0.0.1")
    labelPort = Label(win2,text="Port: ")
    portEntry = Entry(win2)
    labelPort.pack()
    portEntry.pack()
    portEntry.insert(0, "12345")
    labelNick = Label(win2,text="Nickname: ")
    nickEntry = Entry(win2)
    labelNick.pack()
    nickEntry.pack()
    nickEntry.insert(0, "Anonymous")
    Button(win2,text="Save",command=save).pack()
def connect():
    global c
    c = Client(host, port, nickname)
    thread.start_new_thread(startClient, ())
def disconnect():
    global c
    
def startClient():
    global c
    while 1:
        c.Loop()
        sleep(0.001)
    
root = Tk()
def quit(event):
    root.quit()
def commaPref(event):
    showPref()
root.bind("<Alt-q>", quit)
root.bind("<Alt-comma>",commaPref)
menuBar = Menu(root)
fileMenu = Menu(menuBar, tearoff=False)
menuBar.add_cascade(label = "File", underline = 0, menu = fileMenu)
fileMenu.add_command(label="Preferences", command = showPref)
fileMenu.add_command(label="QUIT",underline=1,command = root.quit)
root.config(menu=menuBar)

widget = Console(root)
widget.pack(side=TOP,expand=YES,fill=BOTH)

entry = Entry()
entry.bind("<Return>", sendStuffEvent, ())
entry.pack()

b = Button(text="SEND!",command=sendStuff)
b.pack()
connect = Button(text="CONNECT!",command=connect)
disconnect = Button(text="DISCONNECT!",command=disconnect)
connect.pack()
disconnect.pack()


scrollbar = Scrollbar()
scrollbar.pack(side=RIGHT, fill=Y)

widget.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=widget.yview)

root.mainloop()