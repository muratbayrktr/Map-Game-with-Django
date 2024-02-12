import socket
import sys,os
from auth import Auth
from threading import Thread,Lock,Condition
from agents import RDAgent,WRAgent,CNFAgent,Chat
from utils.catalogue import Catalogue
import uuid

def is_valid_uuid(val):
    try:
        return uuid.UUID(str(val))
    except ValueError:
        return None
    
class Client(Thread):
    def __init__(self, conn, addr, choice, username, password):
        self.chat = Chat()
        self.conn = conn
        self.addr = addr
        self.notexit = True
        self.lock = Lock()
        self.client = Condition(self.lock)
        self.after = 0
        self.choice = choice
        self.username = username
        self.password = password
        self.id = Catalogue()._instance.create_object(self, conn, addr, choice, username, password)
        self.player_id = None
        Thread.__init__(self)

    def run(self):
        print("New connection from",addr)
        # Create agents
        rd = RDAgent(conn, addr, self.chat)
        wr = WRAgent(conn, addr, self.chat)
        cnf = CNFAgent(self.chat, self.client, self.lock)
        rd.start()
        wr.start()
        cnf.start()

        self.authenticate()


        while self.notexit:

            # Wait for message
            self.lock.acquire()
            self.client.wait()
            self.lock.release()
            # Get messages
            messages = self.chat.getin(self.after)
            self.after += len(messages)
            messages = [x.decode() for x in messages]
            
            # Handle messages
            for mess in messages:
                print(mess.split('\n'))
                for tinymess in mess.split('\n'):
                    self.handle_call(tinymess)


        # Join agents
        rd.join()
        wr.join()
        # cnf.join()
        print("Connection closed from",addr)
        conn.close()

    def authenticate(self):

        if self.choice == '1':
            self.chat.newout("authenticate,{},{},{}".format(self.id, self.username, self.password).encode())
        elif self.choice == '2':
            self.chat.newout("signup,{},{},{}".format(self.id, self.username, self.password).encode())
        else:
            print("Invalid choice")
            conn.close()
            sys.exit(1)

    def fight(self, *args):
        mid,mname,oid,oname = args
        print("You are fighting with {}({})".format(oname,oid))

    def setId(self, id):
        self.id = is_valid_uuid(id)

    def info(self, *args):
        print("Info:",*args)#[x for x in args])

    def query(self, *args):
        # *args is an iterator of (id, name, type, x, y)
        print("Player sees:")
        for x in args:
            print(x)

    def team_query(self, *args):
        # *args is an iterator of (id, name, type, x, y)
        print("Team sees:")
        for x in args:
            print(x)

    def handle_call(self, inp):
        f, *args = inp.split(',')
        try:
            if hasattr(Auth,f):
                # Authentication
                print(f"Authenticating with {f}({args})")
                auth = getattr(Auth,f)(*args)
                if not auth:
                    print("Authentication failed")
                    sys.exit(1)
                else:
                    print("Authentication successful")
                    print("Welcome to the game! ")
                    print("Uuid:",self.id)
                    print("You can move with arrow keys and say something by typing and pressing enter.")
            elif hasattr(self,f):
                getattr(self,f)(*args)
            else:
                pass
        except AttributeError:
            print("No such function")
        except TypeError:
            print("Wrong number of arguments")
        except Exception as e:
            print(e)
            print("Unknown error")



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 ... <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ('localhost', port)
    conn.connect(addr)

    choice = input("1. Login\n2. Sign Up\n>")
    username = input("Username: ")
    password = input("Password: ")

    player = Client(conn, addr, choice, username, password)
    player.start()

    while True:
        # Pressed key
        key = input("> ")
        f, *args = key.split(' ')
        if key == 'q':
            player.notexit = False
            player.join()
            break
        else:
            if args != []:
                player.chat.newout(f"{f},{player.id},{','.join(args)}".encode())
            else:
                player.chat.newout(f"{f},{player.id}".encode())
        
        
    conn.close()




        



