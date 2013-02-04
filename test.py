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
    def __init__(self, host, port):
        self.Connect((host, port))
        nick = raw_input()
        connection.Send({"action": "nickname", "nickname": nick})
        # launch our threaded input loop
        #t = start_new_thread(self.InputLoop, ())
    
    def Loop(self):
        connection.Pump()
        self.Pump()
    
    '''def InputLoop(self):
        global players
        
        # horrid threaded input loop
        # continually reads from stdin and sends whatever is typed to the server
        while 1:
            msg = raw_input()
            if msg.startswith("/"):
                cmd = msg[1:]
                if cmd.lower().startswith("pm"):
                    to = cmd[3:].split(" ", 1)[0]
                    msg = cmd[3:].split(" ", 1)[1]
                    if to in players:
                        connection.Send({"action": "PM", "to": to, "message":msg})
                    else:
                        print "That person is not online!"
                        continue
                elif cmd.lower().startswith("name"):
                    newName = cmd[5:]
                    connection.Send({"action":"nickname","nickname":newName})
            else:
                connection.Send({"action": "message", "message": msg})
    '''
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
c = Client("localhost", 12345)


def sendStuff():
    global widget
    global entry
    c.send(entry.get())
    entry.delete(0,END)
    widget.yview(END)
def startClient():
    global c
    while 1:
        c.Loop()
        sleep(0.001)
thread.start_new_thread(startClient, ())
root = Tk()
widget = Console(root)
widget.pack(side=TOP,expand=YES,fill=BOTH)
entry = Entry()
entry.pack()
b = Button(text="SEND!",command=sendStuff)
b.pack()

scrollbar = Scrollbar()
scrollbar.pack(side=RIGHT, fill=Y)

widget.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=widget.yview)

root.mainloop()