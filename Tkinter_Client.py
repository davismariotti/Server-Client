'''
Created on Jan 22, 2013

@author: Davis Mariotti
'''
import Tkinter
from Tkinter import *
import sys
from time import sleep
from sys import stdin, exit
from PodSixNet.Connection import connection, ConnectionListener
from thread import *
class Client(ConnectionListener):
    global players
    players = []
    def __init__(self, host, port):
        print "Enter your nickname:",
        nick = raw_input()
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
start_new_thread(startClient, ())
"""
#---------------------------------------------------------------#
global c
def makeClient():
    global c
    c = Client("localhost", 12345)
    while 1:
        c.Loop()
        sleep(0.001)
def showText(event):
    print box.get()
    box.delete(0, Tkinter.END)
def addTextEvent(event):
    addText(box.get())
def addText(text):
    text.insert(END, "\n"+text)
    box.delete(0, Tkinter.END)
    text.yview(END)
def start(master):
    start_new_thread(makeClient, ())
    frame = Frame(master)
    frame.pack()
    
    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    text = Text(frame)
    text.pack(side=LEFT)
    
    text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text.yview)
    
    box = Entry()
    box.config(width=80)
    box.pack()
    box.bind("<Return>", addText)
        
root = Tk()
root.title("CHAT")
start(root)
root.mainloop()"""