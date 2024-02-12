import socket
import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from auth import Auth
from threading import Thread,Lock,Condition
from agents import RDAgent,WRAgent,Chat


# THIS SCRIPT IS FOR INTERACTIVELY TESTING THE CHARACTER THROUGH THE TERMINAL
# LIKE A GDB... BUT FOR THE CHARACTER
# COMMANDS WILL BE SENT THROUGH CHAT

# EXAMPLE:
# >additem obj2231 Itemname "item long description" 10 2.5
# TRANSLATED INTO:
# find('obj2231').additem('Itemname','item long description', 10,2.5) function call
lock = Lock()
conlock = Lock()
newmess = Condition(lock)
buf = []
def notifications(conn):
    global buf
    conlock.acquire()
    mess = conn.recv(1024).decode()
    print(buf)
    conlock.release()
    while mess:
        lock.acquire()
        buf.append(mess)
        newmess.notify_all()
        lock.release()
        conlock.acquire()
        mess = conn.recv(1024).decode()
        conlock.release()



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 test_chatsrv.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    player1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    player1.connect(('localhost', port))
    notifications_thread = Thread(target=notifications, args=(player1,))
    notifications_thread.start()
    print("1. Login\n2. Sign Up\n>")
    choice = input()
    if choice == '1':
        username = input("Username: ")
        password = input("Password: ")
        player1.sendall("authenticate,,{},{}".format(username, password).encode())
        lock.acquire()
        newmess.wait()
        auth = buf.pop()
        lock.release()
        if auth != "Authentication successful":
            print("Invalid username or password")
            print(auth)
            print(buf)
            notifications_thread.join()
            sys.exit(1)

    elif choice == '2':
        username = input("Username: ")
        password = input("Password: ")
        player1.sendall("signup,,{},{}".format(username, password).encode())
        lock.acquire()
        newmess.wait()
        auth = buf.pop()
        lock.release()
        if auth != "Authentication successful":
            print(auth)
            print(buf)
            sys.exit(1)

    else:
        print("Invalid choice")
        player1.close()
        sys.exit(1)

    while True:
        mess = input(">")
        player1.sendall(mess.encode())



