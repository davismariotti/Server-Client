import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)
    
    def Close(self):
        self._server.DelPlayer(self)
    
    ##################################
    ### Network specific callbacks ###
    ##################################
    def getPlayer(self, str):
       for p in self._server.players:
           if p.nickname == str:
               return p
    def Network_message(self, data):
            self._server.SendToAll({"action": "message", "message": data['message'], "from": self.nickname})
            nicks = []
            for p in self._server.players:
                nicks.append(p.nickname)
            self._server.SendToAll({"action":"players", "players": nicks})
            print self.nickname + ": " + data['message']
            
    def Network_nickname(self, data):
        self.nickname = data['nickname']
        self._server.SendPlayers()
        
    def Network_PM(self, data):
        message = data['message']
        to = data['to']
        PMfrom = self
        p = self.getPlayer(to)
        p.Send({"action":"PMrecieve", "message":message, "from": self.nickname})
        PMfrom.Send({"action":"PMsuccess", "success":True})
class ChatServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        print 'Server launched'
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print "New Player: "+str(player.addr)
        self.players[player] = True
        self.SendToAll({"action":"serverMessage","message":player.nickname + " connected!"})
        self.SendPlayers()
    
    def DelPlayer(self, player):
        print "Deleting Player: " +str(player.addr)
        del self.players[player]
        self.SendPlayers()
    
    def SendPlayers(self):
        nicks = []
        for p in self.players:
            nicks.append(p.nickname)
        self.SendToAll({"action": "players", "players": nicks})
    
    def SendToAll(self, data):
        [p.Send(data) for p in self.players]
    
    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

# get command line argument of server, port
s = ChatServer(localaddr=("localhost", 12345))

s.Launch()
