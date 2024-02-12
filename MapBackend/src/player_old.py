import socket
import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from auth import Auth
from threading import Thread,Lock,Condition
from agents import RDAgent,WRAgent,Chat



def auth_user(chat, username, password, auth_type):
    # Send authentication request
    chat.newmessage("{},,{},{}".format(auth_type,username, password))
    # Wait for response
    messages = chat.getmessages()
    auth = messages[-1].decode()

    if auth != "Authentication successful":
        print("Invalid username or password")
        conn.close()
        sys.exit(1)

def authenticate(chat):
    choice = input("1. Login\n2. Sign Up\n>")
    username = input("Username: ")
    password = input("Password: ")
    if choice == '1':        
        auth_user(chat, username, password, "authenticate")
    elif choice == '2':
        auth_user(chat, username, password, "signup")
    else:
        print("Invalid choice")
        conn.close()
        sys.exit(1)



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 ... <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(('localhost', port))

    chat = Chat()

    rd = RDAgent(conn, ('localhost', port), chat)
    wr = WRAgent(conn, ('localhost', port), chat)

    rd.start()
    wr.start()

    authenticate(chat)
 

    while True:
        mess = input(">")
        conn.sendall(mess.encode())



