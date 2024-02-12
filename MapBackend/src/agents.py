from threading import Thread,Lock,Condition
from utils.catalogue import Catalogue
from auth import Auth

class Chat:
    def __init__(self):
        self.incoming = []
        self.outgoing = []
        self.inl = Lock()
        self.outl = Lock()
        self.newmessout = Condition(self.outl)
        self.newmessin = Condition(self.inl)

    def yellout(self):
        self.outl.acquire()
        self.newmessout.notify_all()
        self.outl.release()

    def silentnewout(self,mess):
        self.outl.acquire()
        # if mess is list:
        self.outgoing.append(mess)
        self.outl.release()

    def newout(self,mess):
        self.outl.acquire()
        # if mess is list:
        self.outgoing.append(mess)
        # print("Put into outbox.")
        self.newmessout.notify_all()
        self.outl.release()

    def newin(self,mess):
        self.inl.acquire()
        self.incoming.append(mess)
        # print("Put into inbox.")
        # print("message:", mess)
        self.newmessin.notify_all()
        # print("Newmessin notified.")
        self.inl.release()

    def getout(self,after=0):
        self.outl.acquire()
        if len(self.outgoing) < after:
            a = []
        else:
            a = self.outgoing[after:]
        self.outl.release()
        return a
        
    def getin(self,after=0):
        self.inl.acquire()
        if len(self.incoming) < after:
            a = []
        else:
            a = self.incoming[after:]
        self.inl.release()
        return a
    

# SVAgent = Server Agent waits on the chat buffer and notifies the server when message is received
class SVAgent(Thread):
    def __init__(self, chat, server, slock):
        self.chat = chat
        self.slock = slock
        self.server = server # Server condition variable
        Thread.__init__(self)
        
    def run(self):
        while True:
            self.chat.inl.acquire()
            # print("SVAgent waiting.")
            self.chat.newmessin.wait()
            # print("SVAgent notified.")
            self.chat.inl.release()
            self.slock.acquire()
            self.server.notify_all()
            self.slock.release()

# CNFAgent = Client Notification Forwarding Agent waits on the chat buffer and notifies the client when message is received
class CNFAgent(Thread):
    def __init__(self, chat, client, clock):
        self.chat = chat
        self.clock = clock
        self.client = client # Client condition variable
        Thread.__init__(self)
        
    def run(self):
        while True:
            self.chat.inl.acquire()
            # print("CNFAgent waiting.")
            self.chat.newmessin.wait()
            # print("CNFAgent notified.")
            self.chat.inl.release()
            self.clock.acquire()
            self.client.notify_all()
            self.clock.release()
		
    

class RDAgent(Thread):
    def __init__(self, conn, addr, chat):
        self.conn = conn
        self.claddr = addr
        self.chat = chat
        Thread.__init__(self)

        
    def run(self):
        print("Read Agent connected to",self.claddr)
        inp = self.conn.recv(1024)
        print("Read agent received.")
        while inp:
            self.chat.newin(inp)
            inp = self.conn.recv(1024)
        # print('client is terminating')
        self.conn.close()


class WRAgent(Thread):
    def __init__(self, conn, addr, chat):
        self.conn = conn
        self.claddr = addr
        self.chat = chat
        self.current = 0
        Thread.__init__(self)
		
    def run(self):
        # print("Write Agent connected to",self.claddr)
        oldmess = self.chat.getout()
        self.current += len(oldmess)
        self.conn.send('\n'.join([i.decode() for i in oldmess]).encode())
        notexit = True
        while notexit:
            self.chat.outl.acquire()
            # print("Write agent waiting.")
            self.chat.newmessout.wait()
            # print("Write agent notified.")
            self.chat.outl.release()
            oldmess = self.chat.getout(self.current)
            self.current += len(oldmess)
            try:
                # print("Write agent sent.")
                self.conn.send('\n'.join([i.decode() for i in oldmess]).encode())
            except:
                notexit = False