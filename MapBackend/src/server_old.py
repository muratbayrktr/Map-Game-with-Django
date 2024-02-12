#!/usr/bin/python

from agents import RDAgent,WRAgent,Chat
from threading import Thread,Lock,Condition
import socket
import sys
import time
from auth import Auth
from utils.catalogue import Catalogue


database_lock = Lock()

def handle_call(inp):
    f, id, *args = inp.split(',')
    try:
        getattr(Catalogue.attach(id), f)(*args)
    except AttributeError:
        print("No such function")
    except TypeError:
        print("Wrong number of arguments")
    except Exception as e:
        print(e)
        print("Unknown error")

def handle_bulk(oldmess):
    print(oldmess)
    for mess in oldmess:
        print("handling",mess.decode())
        handle_call(conn, mess.decode())

def handle_auth(conn,messages):
    for inp in messages:
        f, id, *args = inp.split(',')
        if hasattr(Auth,f):
            # Authentication
            database_lock.acquire()
            auth = getattr(Auth,f)(*args)
            database_lock.release()
            if not auth:
                conn.send("Authentication failed".encode())
                conn.close()
                return False
            else:
                conn.send("Authentication successful".encode())
                return True

def check_authentications(rooms):
    for (conn,addr),chat in rooms.items():
        current = 0
        oldmess = chat.getmessages()
        handle_auth(conn,oldmess)
        current += len(oldmess)
        notexit = True
        while notexit:
            chat.lock.acquire()
            chat.newmess.wait()
            chat.lock.release()
            oldmess = chat.getmessages(current)
            handle_auth(conn, oldmess)
            current += len(oldmess)
            try:
                print("Write agent sent.")
            except:
                notexit = False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ',sys.argv[0],'port')
        sys.exit(-1)


    HOST = ''
    PORT = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    
    rooms = {}

    n = Thread(target=check_authentications, args=(rooms,))
    n.start()

    connections = []

    while True:
        # Accept users
        conn, addr = s.accept()
        connections.append(conn)
        print('Connected by', addr)

        chatroom = Chat()
        rooms[(conn,addr)] = chatroom

        credentials = conn.recv(1024).decode()
        auth = handle_auth(conn, credentials)
        if not auth:
            conn.send("Authentication failed".encode())
            conn.close()
            continue
        else:
            conn.send("Authentication successful".encode())
            rd = RDAgent(conn,addr,chatroom)
            wr = WRAgent(conn,addr,chatroom)

            # Start them
            rd.start()
            wr.start()
    else:
        # Wait for them to finish
        rd.join()
        wr.join()
        n.join()
        conn.close()
