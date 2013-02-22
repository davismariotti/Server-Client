'''
Created on Jan 7, 2013

@author: Davis Mariotti
'''
from PodSixNet.Connection import connection, ConnectionListener
from Tkinter import *
from thread import *
from time import *
import Tkinter, Queue, thread, os, time, tkFileDialog

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
    def getPlayers(self):
        return self.players
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
    def sendData(self, data):
        connection.Send(data)
    #######################################
    ### Network event/message callbacks ###
    #######################################
    
    def Network_players(self, data):
        global players
        #Recieved list of players.
        self.players = data['players']
        listbox.delete(0, Tkinter.END)
        for p in self.getPlayers():
            listbox.insert(END,p)
    def Network_message(self, data):
        #Got a message.
        #print data['from'] + ": " + data['message']
        thread.start_new(toTextBox, (widget, data['from']+": "+data['message']))
    def Network_listRecieve(self, data):
        thread.start_new(toTextBox, (widget,"Clients: "+data['players']))
    def Network_serverMessage(self, data):
        msg = data['message']
        thread.start_new(toTextBox, (widget,"Server: "+msg))
    def Network_PMrecieve(self, data):
        msg = data['message']
        of = data['from']
        thread.start_new(toTextBox, (widget,"PM from " + of + ": " + msg))
    def Network_PMsuccess(self, data):
        success = data['success']
        if success:
            thread.start_new(toTextBox, (widget,"PM successfully sent!"))
        else:
            thread.start_new(toTextBox, (widget,"Error, recipient may not be online."))
    def Network_connected(self, data):
        print "You are now connected to the server"
    
    def Network_error(self, data):
        print 'error:', data['error'][1]
        connection.Close()
    
    def Network_disconnected(self, data):
        print 'Server disconnected'
        exit()

def command(cmd):
    if cmd.startswith("nick"):
        c.sendData({"action":"nickname","nickname":cmd[5:]})
    elif cmd.startswith("pm"):
        args = []
        args = cmd[3:].split()
        to = args[0]
        message = ""
        message = message.join(args[1:])
        c.sendData({"action":"PM","to":to,"message":message})
    elif cmd.startswith("list"):
        c.sendData({"action":"list"})
        
def pmFromBox():
    p = listbox.get(Tkinter.ACTIVE)
    entry.insert(END, "/pm "+p+" ")
def sendStuff():
    global widget
    global entry
    global c
    text = ""
    text = entry.get()
    if text != "":
        if text.startswith("/"):
            command(text[1:])
        else:
            c.send(entry.get())
    entry.delete(0,END)
    widget.yview(END)
def sendStuffEvent(event):
    sendStuff()
global host, port, nickname    
host = "127.0.0.1"
port = 12345
nickname = "Anonymous"

def disconnect():
    global c
    c.sendData({"action":"disconnect"})
    
def startClient():
    global c
    while 1:
        #Try except stops exception when quitting
        try:
            c.Loop()
            sleep(0.001)
        except:
            pass
def connect():
    global c
    c = Client(host, port, nickname)
    thread.start_new_thread(startClient, ())
    send.config(state="normal")
    connect.config(state="disabled")
    disconnect.config(state="normal")
    entry.config(state="normal")
    listbox.config(state="normal")
    pm.config(state="normal")
def showPref():
    global host, port, nickname
    def save():
        global host, port, nickname
        host = hostEntry.get()
        port = int(portEntry.get())
        nickname = nickEntry.get()
        win2.destroy()
    win2 = Tk()
    labelHost = Label(win2,text="Host: ")
    hostEntry = Entry(win2)
    labelHost.pack()
    hostEntry.pack()
    hostEntry.insert(0, host)
    labelPort = Label(win2,text="Port: ")
    portEntry = Entry(win2)
    labelPort.pack()
    portEntry.pack()
    portEntry.insert(0, port)
    labelNick = Label(win2,text="Nickname: ")
    nickEntry = Entry(win2)
    labelNick.pack()
    nickEntry.pack()
    nickEntry.insert(0, nickname)
    Button(win2,text="Save",command=save).pack()

def about():
    def close():
        aboutWindow.destroy()
    aboutWindow = Tk()
    aboutWindow.geometry("150x50")
    label = Label(aboutWindow,text="Made by Davis Mariotti")
    label.pack()
    b = Button(aboutWindow,text="OK", command = close)
    b.pack()

def quit(event):
    root.quit()
def commaPref(event):
    showPref()
def openFileEvent(event):
    openLogs()
def saveFileEvent(event):
    saveLogs()
root = Tk()
def saveLogs():
    dialog = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
    text = widget.get(1.0, END)
    dialog.write(text)
    dialog.close()
def openLogs():
    file = tkFileDialog.askopenfile(mode='r',initialdir="C:\\")
    text = file.read()
    newWindow = Tk()
    textBox = Text(newWindow)
    textBox.pack()
    textBox.insert(END, text)
def makeMenu():
    menuBar = Menu(root)
    fileMenu = Menu(menuBar, tearoff=False)
    aboutMenu = Menu(menuBar, tearoff=False)
    menuBar.add_cascade(label = "File", underline = 0, menu = fileMenu)
    menuBar.add_cascade(label="About", underline = 0, menu = aboutMenu)
    fileMenu.add_command(label="Open", command=openLogs)
    fileMenu.add_command(label="Save", command=saveLogs)
    fileMenu.add_command(label="QUIT",underline=1,command = root.quit)
    aboutMenu.add_command(label="About",command = about)
    aboutMenu.add_command(label="Preferences", command = showPref)
    return menuBar
root.bind("<Alt-q>", quit)
root.bind("<Alt-comma>",commaPref)
root.bind("<Alt-o>", openFileEvent)
root.bind("<Alt-s>", saveFileEvent)

root.config(menu=makeMenu())
f = Frame(root)
f.pack()
yscrollbar = Scrollbar(f)
yscrollbar.pack(side=RIGHT, fill=Y)

widget = Console(f,yscrollcommand=yscrollbar.set)
widget.pack(side=TOP,expand=YES,fill=BOTH)
yscrollbar.config(command=widget.yview)

entry = Entry(state="disabled",width=40)
entry.bind("<Return>", sendStuffEvent, ())
entry.pack()

send = Button(text="SEND!",command=sendStuff, state="disabled")
send.pack()
connect = Button(text="CONNECT!",command=connect)
disconnect = Button(text="DISCONNECT!",command=disconnect,state="disabled")
connect.pack()
disconnect.pack()
listbox = Listbox(root, state="disabled")
listbox.pack()
pm = Button(root,text="PM USER",command=pmFromBox, state="disabled")
pm.pack()


root.mainloop()