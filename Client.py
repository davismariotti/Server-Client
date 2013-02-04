import sys
from time import sleep
from sys import stdin, exit
from Tkinter import *
import Tkinter



# This example uses Python threads to manage async input from sys.stdin.
# This is so that I can receive input from the console whilst running the server.
# Don't ever do this - it's slow and ugly. (I'm doing it for simplicity's sake)
from thread import *
class App:
        def __init__(self, master, connection):
            self.connection = connection
            self.frame = Frame(master)
            self.frame.pack()
            self.connection.Send({})
