'''
@author: denizalti
@note: The Leader
'''
from optparse import OptionParser
from threading import Thread, Lock, Condition
from utils import *
from communicationutils import *
from connection import *
from group import *
from peer import *
from message import *
from acceptor import *
from scout import *
from commander import *
from bank import *

parser = OptionParser(usage="usage: %prog -p port -b bootstrap")
parser.add_option("-p", "--port", action="store", dest="port", type="int", default=4448, help="port for the node")
parser.add_option("-b", "--boot", action="store", dest="bootstrap", help="address:port tuple for the bootstrap peer")
(options, args) = parser.parse_args()

# TIMEOUT THREAD
class Replica():
    def __init__(self, id, port, bootstrap=None):
        self.addr = findOwnIP()
        self.port = port
        self.id = createID(self.addr,self.port)
        self.type = REPLICA
        self.toPeer = Peer(self.id,self.addr,self.port,self.type)
        # groups
        self.acceptors = Group(self.toPeer)
        self.replicas = Group(self.toPeer)
        self.leaders = Group(self.toPeer)
        # Exit
        self.run = True
        # Bank
        self.bank = Bank()
        # print some information
        print "IP: %s Port: %d ID: %d" % (self.addr,self.port,self.id)
        if bootstrap:
            connectToBootstrap(self,bootstrap)
        # Start a thread with the server which will start a thread for each request
        server_thread = Thread(target=self.serverLoop)
        server_thread.start()
        # Start a thread that waits for inputs
        input_thread = Thread(target=self.getInputs)
        input_thread.start()
        
    def __str__(self):
        returnstr = "State of Replica %d\n" %self.id
        returnstr += "IP: %s\n" % self.addr
        returnstr += "Port: %d\n" % self.port
        returnstr += "Acceptors:\n%s" % self.acceptors
        returnstr += "Leaders:\n%s" % self.leaders
        returnstr += "Replicas:\n%s" % self.replicas
        return returnstr
        
    def serverLoop(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind((self.addr,self.port))
        s.listen(10)
#        s.settimeout(10)
        while self.run:
            try:
                clientsock,clientaddr = s.accept()
#                print "DEBUG: Accepted a connection on socket:",clientsock," and address:",clientaddr
                # Start a Thread
                Thread(target=self.handleConnection,args =[clientsock]).start()
            except KeyboardInterrupt:
                break
        s.close()
        return
        
    def handleConnection(self,clientsock):
#        print "DEBUG: Handling the connection.."
        addr,port = clientsock.getpeername()
        connection = Connection(addr,port,reusesock=clientsock)
        message = Message(connection.receive())
        if message.type == MSG_HELO:
            messageSource = Peer(message.source[0],message.source[1],message.source[2],message.source[3])
            if messageSource.type == CLIENT:
                replymessage = Message(type=MSG_HELOREPLY,source=self.toPeer.serialize())
            else:
                replymessage = Message(type=MSG_HELOREPLY,source=self.toPeer.serialize(),acceptors=self.acceptors.toList(),\
                                   leaders=self.leaders.toList(),replicas=self.replicas.toList())
            newmessage = Message(type=MSG_NEW,source=self.toPeer.serialize(),newpeer=messageSource.serialize())
            connection.send(replymessage)
            # Broadcasting MSG_NEW without waiting for a reply.
            # To add replies, first we have to add MSG_ACK & MSG_NACK
            self.acceptors.broadcastNoReply(newmessage)
            self.leaders.broadcastNoReply(newmessage)
            self.replicas.broadcastNoReply(newmessage)
            if messageSource.type == ACCEPTOR:
                self.acceptors.add(messageSource)
            elif messageSource.type == LEADER:
                self.leaders.add(messageSource)
            elif messageSource.type == REPLICA:
                self.replicas.add(messageSource)
        elif message.type == MSG_HELOREPLY:
            self.leaders.mergeList(message.leaders)
            self.acceptors.mergeList(message.acceptors)
            self.replicas.mergeList(message.replicas)
        elif message.type == MSG_NEW:
            newpeer = Peer(message.newpeer[0],message.newpeer[1],message.newpeer[2],message.newpeer[3])
            if newpeer.type == ACCEPTOR:
                self.acceptors.add(newpeer)
            elif newpeer.type == LEADER:
                self.leaders.add(newpeer)
            elif newpeer.type == REPLICA:
                self.replicas.add(newpeer)
        elif message.type == MSG_DEBIT:
            randomleader = randint(0,len(self.leaders)-1)
            self.leaders[randomleader].send(message)
        elif message.type == MSG_DEPOSIT:
            randomleader = randint(0,len(self.leaders)-1)
            self.leaders[randomleader].send(message)
        elif message.type == MSG_BYE:
            messageSource = Peer(message.source[0],message.source[1],message.source[2],message.source[3])
            if messageSource.type == ACCEPTOR:
                self.acceptors.remove(messageSource)
            elif messageSource.type == LEADER:
                self.leaders.remove(messageSource)
            else:
                self.replicas.remove(messageSource)
        elif message.type == MSG_PERFORM:
            self.state[message.commandnumber] = message.proposal
            self.bank.executeCommand(message.proposal)
        connection.close()
        
    def getInputs(self):
        while self.run:
            input = raw_input("What should I do? ")
            if len(input) == 0:
                print "I'm listening.."
            else:
                input = input.split()
                input[0] = input[0].upper()
                if input[0] == 'HELP':
                    self.printHelp()
                    self.newCommand(int(commandnumber), proposal)
                elif input[0] == 'STATE':
                    print self
                elif input[0] == 'PAXOS':
                    print self.state
                elif input[0] == 'EXIT':
                    print "So long and thanks for all the fish.."
                    self.die()
                else:
                    print "Sorry I couldn't get it.."
        return
                    
    def die(self):
        self.run = False
        byeMessage = Message(type=MSG_BYE,source=self.toPeer.serialize())
        self.leaders.broadcast(byeMessage)
        self.acceptors.broadcast(byeMessage)
        self.replicas.broadcast(byeMessage)
        self.toPeer.send(byeMessage)
                    
    def printHelp(self):
        print "I can execute a new Command for you as follows:"
        print "To see my Connection State type STATE"
        print "To see my Paxos State type PAXOS"
        print "For help type HELP"
        print "To exit type EXIT"
   
'''main'''
def main():
    theReplica = Replica(options.port,options.bootstrap)

'''run'''
if __name__=='__main__':
    main()

  


    
