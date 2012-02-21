"""
@author: Deniz Altinbuken, Emin Gun Sirer
@note: RLock Coordination Object
@date: March 20, 2011
@copyright: See LICENSE
"""
from threading import Lock
from concoord.exception import *

class DRlock():
    def __init__(self):
        self.lockcount = 0
        self.holder = None
        self.queue = []
        self.atomic = Lock()
    
    def acquire(self, kwargs):
        _concoord_designated, _concoord_owner, _concoord_command = kwargs['_concoord_designated'], kwargs['_concoord_owner'], kwargs['_concoord_command']
        with self.atomic:
            if self.lockcount > 0 and self.holder != _concoord_command.client:
                self.queue.append(_concoord_command)
                raise UnusualReturn
            elif self.lockcount > 0 and self.holder == _concoord_command.client:
                self.lockcount += 1                
            else:
                self.lockcount = 1
                self.holder = _concoord_command.client

    def release(self, kwargs):
        _concoord_designated, _concoord_owner, _concoord_command = kwargs['_concoord_designated'], kwargs['_concoord_owner'], kwargs['_concoord_command']
        with self.atomic:
            if self.lockcount > 0:
                self.lockcount -= 1
            else:
                return "Release on unacquired lock"
            
            if self.lockcount == 0 and len(self.queue) > 0:
                self.lockcount += 1
                newcommand = self.queue.pop(0)
                self.holder = newcommand.client
                # return to new holder which is waiting
                return_outofband(_concoord_designated, _concoord_owner, newcommand)
            elif self.lockcount == 0 and len(self.queue) == 0:
                self.holder = None
                self.lockcount = False
            else:
                pass
                
    def __str__(self):
        return "Distributed RLock\nholder: %s\nqueue: %s\n" % (self.holder, " ".join([str(m) for m in self.queue]))