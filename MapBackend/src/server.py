from agents import RDAgent,WRAgent,SVAgent,Chat
from threading import Thread,Lock,Condition
import socket
import sys
import time
import uuid
from auth import Auth
from utils.catalogue import Catalogue
from utils.config import Config
from objects import Player
from map import Map, TeamMap
from database import Database
import json
import base64
from PIL import Image
import io




def is_valid_uuid(val):
    try:
        return uuid.UUID(str(val))
    except ValueError:
        return None
    
# Global rooms dictionary
class Rooms:
    def __init__(self):
        self.rooms = {}
        self.lock = Lock()

    def new_chatroom(self, id, chat):
        self.lock.acquire()
        self.rooms[id] = chat
        self.lock.release()

    def get_chatroom(self, id):
        self.lock.acquire()
        try:
            return self.rooms[id]
        except KeyError:
            return None
        finally:
            self.lock.release()

    def get_room_rep(self) -> str:
        self.lock.acquire()
        repres = str(self.rooms)
        self.lock.release()
        return repres

rooms = Rooms()

mess = lambda : {
    "f": None,
    "id": None,
    "args": None,
    "query_result": None,
    "image": None,
    "vision_x": None,
    "vision_y": None
}



class Server(Thread):
    def __init__(self, conn, addr, dblock):
        self.chat = Chat()
        self.conn = conn
        self.addr = addr
        self.notexit = True # Will be altered by the client
        self.lock = Lock()
        self.dblock = Lock() #dblock
        self.server = Condition(self.lock)
        self.after = 0
        self.username = None
        self.user_uuid = None
        self.player = None
        self.GMAP = None
        self.TMAP = None
        Thread.__init__(self)

    def run(self):
        print("New connection from",self.addr)
        inp = self.conn.recv(1024)
        while inp:
            # Handle input
            self.handle_call(inp.decode())
            inp = self.conn.recv(1024)

        # print("Connection closed from",self.addr)
        self.conn.close()
        print("Connection closed from",self.addr)

    def handle_call(self, inp):
        print(inp)
        f, id, *args = inp.split(',')
        if getattr(Auth,"auth_with_token")(id):
            try:
                if hasattr(self,f):
                    # Call function
                    if args != []:
                        print(f"Calling {f}({args})")
                        getattr(self,f)(*args)
                    else:
                        print(f"Calling {f}()")
                        getattr(self,f)()
                else:
                    obj = Catalogue().attach(is_valid_uuid(id))
                    self_query, team_query, notify_all, image_path, x_discovered, y_discovered = getattr(obj,f)(*args) 
                    query_result = list(self_query)
                    team_query_result = list(team_query)
                    print(query_result, team_query_result, notify_all)
                    # if notify_all:
                    #     ids = rooms.rooms.keys()
                    #     for room in ids:
                    #         rooms.get_chatroom(room).newout(f"team_query,{team_query_result}".encode())
                    merged_query = self.merge_team_with_player_vision(query_result, team_query_result)
                    if self_query is not None:
                        MESS = mess()
                        MESS["f"] = "query"
                        MESS["id"] = id
                        # Convert every uuid to hex in the tuples in the list
                        MESS["query_result"] = [[x.hex if isinstance(x, uuid.UUID) else x for x in y] for y in merged_query]
                        MESS["image"] = image_path
                        MESS["vision_x"] = x_discovered
                        MESS["vision_y"] = y_discovered
                        self.conn.sendall(json.dumps(MESS).encode())
                        # self.notify_fight(query_result)
            except AttributeError as e:
                print(e)
                print("No such function")
                self.conn.sendall("No such function".encode())
            except TypeError as e:
                print(e)
                print(f"Wrong arguments for {f}: {args}")
                print("Wrong number of arguments")
                self.conn.sendall("Wrong number of arguments".encode())
            except Exception as e:
                print(e)
                print("Unknown error")
                self.conn.sendall("Unknown error".encode())
            finally:
                Catalogue().dump()
                return True
        else:
            self.conn.sendall("Authentication failed.".encode())

    @staticmethod
    def merge_team_with_player_vision(self_query, team_query):
        # Merges two lists of tuples into one list of tuples
        # If there is a tuple with the same id in both lists, the tuple in the self_query will be used
        # If there is a tuple with the same id in only one list, that tuple will be used
        for team_tuple in team_query:
            if team_tuple[0] not in [x[0] for x in self_query]:
                self_query.append(team_tuple)
        return self_query

    def notify_fight(self, rval):
        def adjacent(pos1, pos2):
            x1, y1 = pos1
            x2, y2 = pos2
            return abs(x1-x2) <= 1 and abs(y1-y2) <= 1

        for id, name, type, x, y in rval:
            if type == 'Player' and id != self.player_id and adjacent(self.player.position, (x,y)) and self.player.team.name != Catalogue().attach(id).team.name:
                print(f"fight between {self.player.name} and {name}")
                # Notify both players
                # Notify self
                self.conn.sendall(f"fight,{self.player_id},{self.player.name},{id},{name}".encode())
                # Notify other
                rooms.get_chatroom(id).newout(f"fight,{id},{name},{self.player_id},{self.player.name}".encode())


    # When user enters save command, current state of user will be dumped to database
    
    def save(self):    
        print("Saving to database")
        # Save to database
        self.dblock.acquire()
        db = Database()
        print(self.player_id.hex, self.username)
        db.execute("UPDATE users SET player_uuid=? WHERE username=?", (self.player_id.hex, self.username))
        self.dblock.release()


    def load(self):
        
        db = Database()
        player_uuid = db.fetch_one("SELECT player_uuid FROM users WHERE username=?", (self.username,))[0]
        print(player_uuid)
        self.player_id = is_valid_uuid(player_uuid)
        self.player = Catalogue().attach(self.player_id)
        
        # player_map_id = self.player.map.getid()
        

        # self.GMAP = Catalogue().attach(player_map_id)
        # self.TMAP = self.GMAP.teams[self.player.team.name]
        # self.GMAP.players[self.player.name] = self.player
        # print(f"Loaded {self.player.name}({self.player_id}) to map {self.GMAP.name}({self.GMAP.getid()})")
        global rooms
        rooms.new_chatroom(self.player_id, self.chat)
        MESS = mess()
        MESS["f"] = "setId"
        MESS["id"] = self.player_id.hex
        MESS["args"] = self.player_id.hex
        self.conn.sendall(json.dumps(MESS).encode())

        

    def join(self, mapid, username, teamname):
        mapid = is_valid_uuid(mapid)
        if mapid is None:
            self.conn.sendall("info,failiure".encode())
            return
        self.GMAP = Catalogue().attach(mapid)
        self.player = self.GMAP.join(username, teamname)
        self.player_id = self.player.getid()
        self.dblock.acquire()
        db = Database()
        db.execute("UPDATE users SET player_uuid=? WHERE username=?", (self.player_id.hex, self.username))
        self.dblock.release()
        global rooms
        rooms.new_chatroom(self.player_id, self.chat)
        MESS = mess()
        MESS["f"] = "setId"
        MESS["id"] = self.player_id.hex
        MESS["args"] = self.player_id.hex
        self.conn.sendall(json.dumps(MESS).encode())

    def newmap(self, size, name):
        # Save map to database
        query = "INSERT INTO maps (name, width, height, map_uuid) VALUES (?, ?, ?, ?)"
        width, height = list(map(int,size.split('x')))
        self.GMAP = Map(name, (width,height), Config.load(name))
        params = (name, width, height, self.GMAP.getid().hex)
        db = Database()
        self.dblock.acquire()
        db.execute(query, params)
        self.dblock.release()
        Catalogue().save(self.GMAP.getid())
        self.conn.sendall(f"New map {name} created.".encode())

    def listmaps(self):
        objs = Catalogue.listobjects()
        maps = []
        for id,obj in objs:
            # Filter maps
            if isinstance(obj, Map) and not isinstance(obj, TeamMap): 
                # print(obj.name) 
                teams = [x for x in obj.teams.keys()] if obj.teams != {} else []
                if teams == []:
                    maps.append(f"{obj.name},{id.hex}")
                    # self.conn.sendall(f"info,{obj.name},{id.hex}".encode())
                else:
                    maps.append(f"{obj.name},{teams},{id.hex}")
                    # self.conn.sendall(f"info,{obj.name},{str(teams)},{id.hex}".encode())
        
        self.conn.sendall(f"info,{str(maps)}".encode())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ',sys.argv[0],'port')
        sys.exit(-1)

    dblock = Lock()

    
    Catalogue().loadall()

    try:
        print(Catalogue.listobjects())
    except Exception as e:
        print(e)
        print("No objects loaded")
    HOST = ''
    PORT = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    while True:
        # Accept users
        conn, addr = s.accept()
        server = Server(conn, addr, dblock)
        server.start()
