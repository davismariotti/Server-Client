import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

# This example uses Python threads to manage async input from sys.stdin.
# This is so that I can receive input from the console whilst running the server.
# Don't ever do this - it's slow and ugly. (I'm doing it for simplicity's sake)
from thread import *
import Tkinter
from Tkinter import *

class Client(ConnectionListener):
    global players
    players = []
    def __init__(self, host, port):
        class App():
            def __init__(self, master):
                frame = Frame(master)
                frame.pack()
                connection.Send({})
      
        root = Tk()
        root.title("CHAT")
        app = App(root)
        start_new_thread(root.mainloop,())
        print "Enter your nickname:",
        nick = raw_input()
        self.Connect((host, port))
        connection.Send({"action": "nickname", "nickname": nick})
        # launch our threaded input loop
        t = start_new_thread(self.InputLoop, ())
    
    def Loop(self):
        connection.Pump()
        self.Pump()
    
    def InputLoop(self):
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
    
    #######################################
    ### Network event/message callbacks ###
    #######################################
    
    def Network_players(self, data):
        global players
        #Recieved list of players.
        players = data['players']
    
    def Network_message(self, data):
        #Got a message.
        print data['from'] + ": " + data['message']\
        
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
while 1:
    c.Loop()
    sleep(0.001)