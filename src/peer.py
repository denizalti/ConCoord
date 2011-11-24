"""
@author: denizalti
@note: Peer
@date: February 1, 2011
"""
from enums import *
from utils import *

class Peer():
    def __init__(self, peeraddr, peerport, peertype=-1):
        self.type = peertype
        self.port = peerport
        self.addr = peeraddr

    def getid(self):
        return "%s:%d" % (self.addr, self.port)
    
    def __hash__(self):
        return self.getid().__hash__()

    def __eq__(self, otherpeer):
        if otherpeer == None:
            return False
        else:
            return self.getid() == otherpeer.getid()

    def __lt__(self, otherpeer):
        if otherpeer == None:
            return False
        else:
            return self.getid() < otherpeer.getid()

    def __gt__(self, otherpeer):
        if otherpeer == None:
            return False
        else:
            return self.getid() > otherpeer.getid()

    def __ne__(self, otherpeer):
        if otherpeer == None:
            return False
        else:
            return self.getid() != otherpeer.getid()
        
    def __str__(self):
        return '%s PEER(%s:%d)' % (node_names[self.type] if self.type != -1 else "UNKNOWN", self.addr, self.port)