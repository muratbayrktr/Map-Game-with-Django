from typing import Any
from utils.catalogue import Catalogue
from user import UserObserver
from threading import Thread
from time import sleep
import uuid

def is_valid_uuid(val):
    try:
        return uuid.UUID(str(val))
    except ValueError:
        return None
    

class MapObject:
    def __init__(self, name, position, subobj=None):
        self.subobj = subobj
        if self.subobj is None:
            self.subobj = self
        self.position = position
        self.name = name
        self.id = Catalogue()._instance.create_object(self.subobj, name, position)

    def getid(self):
        return self.id



class Mine(MapObject):
    def __init__(self, name, position, p=4, d=5, k=1000):
        super().__init__(name, position, self)
        self.p = p
        self.d = d
        self.k = k


class Health(MapObject):
    def __init__(self, name, position, inf=1, m=20):
        super().__init__(name, position, self)
        self.inf = inf
        self.m = m


class Freezer(MapObject):
    def __init__(self, name, position, p=4, d=5, k=1000):
        super().__init__(name, position, self)
        self.p = p
        self.d = d
        self.k = k



class ObjectFactory:   # Factory Pattern To Create MabObjects
    @staticmethod
    def createObject(name, type, position, *args, **kwargs):
        try:
            if type == 'Mine':
                return Mine(name,position,*args,**kwargs)
            elif type == 'Health':
                return Health(name,position,*args,**kwargs)
            elif type == 'Freezer':
                return Freezer(name,position,*args,**kwargs)
        except Exception as e:
            raise e
        
class Player(MapObject):
    def __init__(self,username,team,health,repo,map):
        super().__init__(username, (5,5), self)
        self.map = map
        self.username = username
        self.team = team
        self.health = health
        self.repo = repo 
        self.playervision = map.config.get("playervision")
        self.facing = 'SE'
        self.canmove = True
        self.activated_bombs = {}

    def move(self, direction):
        """Player moves on a direction (‘N,NW,W,SW,…’)
        on the map. Each move will result on a query
        and image update of the team map""" 
        if not self.canmove:
            return None
        # print(f"{self.username}: Moving {direction}")
        if direction == 'N':
            self.position = (self.position[0], self.position[1] - 10)
        elif direction == 'NE':
            self.position = (self.position[0] + 10, self.position[1] - 10)
        elif direction == 'E':
            self.position = (self.position[0] + 10, self.position[1])
        elif direction == 'SE':
            self.position = (self.position[0] + 10, self.position[1] + 10)
        elif direction == 'S':
            self.position = (self.position[0], self.position[1] + 10)
        elif direction == 'SW':
            self.position = (self.position[0] - 10, self.position[1] + 10)
        elif direction == 'W':
            self.position = (self.position[0] - 10, self.position[1])
        elif direction == 'NW':
            self.position = (self.position[0] - 10, self.position[1] - 10)

        self.facing = direction
        # what should we do with this?
        try:
            Catalogue().attach(self.map.getid()).teammap(self.team.name)
        except Exception as e:
            print(e)
            raise Exception("Team does not exist")
        objectIter, teamIter, notify_all = Catalogue().attach(self.map.getid()).teammap(self.team.name).query(self.getid(),self.position[0], self.position[1], self.playervision)
        
        image = Catalogue().attach(self.map.getid()).getImage(self.position[0], self.position[1], self.playervision)
        
        Catalogue().attach(self.map.getid()).teammap(self.team.name).setImage(self.position[0], self.position[1], self.playervision, image)

        image_path = Catalogue().attach(self.map.getid()).teammap(self.team.name).config.get('image')
        
        Catalogue().attach(self.map.getid()).teammap(self.team.name).x_discovered_until = max(self.position[0] + self.playervision, Catalogue().attach(self.map.getid()).teammap(self.team.name).x_discovered_until)
        Catalogue().attach(self.map.getid()).teammap(self.team.name).y_discovered_until = max(self.position[1] + self.playervision, Catalogue().attach(self.map.getid()).teammap(self.team.name).y_discovered_until)

        x_discovered_until, y_discovered_until = Catalogue().attach(self.map.getid()).teammap(self.team.name).x_discovered_until, Catalogue().attach(self.map.getid()).teammap(self.team.name).y_discovered_until

        # if there is a health object in the nearby map, we should check if the player is close enough to pick it up
        obj_query = list(objectIter)
        for qr in obj_query:
            id, name ,type , x, y = qr
            if self.name in name:
                print(self.name, name)
                continue
            if type == "Health":
                if abs(self.position[0] - x) < 10 and abs(self.position[1] - y) < 10:
                    print("health object found")
                    self.repo.append(("Health", 20))
                    
                    Catalogue().attach(self.map.getid()).removeObject(id)
                    Catalogue().attach(self.map.getid()).teammap(self.team.name).team_vision.pop(is_valid_uuid(id))
                    print(f"{self.username}: Picked up Health")
            if type == "Mine":
                if abs(self.position[0] - x) < 10 and abs(self.position[1] - y) < 10:
                    print("mine object found")
                    damage = Catalogue().attach(self.map.getid()).objects[id][4].d
                    proximity = Catalogue().attach(self.map.getid()).objects[id][4].p
                    bomb_x, bomb_y = Catalogue().attach(self.map.getid()).objects[id][2], Catalogue().attach(self.map.getid()).objects[id][3]
                    
                    # Timer thread to wait for 5 seconds
                    if self.activated_bombs.get(id.hex) is None:
                        self.activated_bombs[id.hex] = True
                        timer = Thread(target=self.mine, args=(damage,bomb_x,bomb_y,proximity, id))
                        timer.start()

            if type == "Freezer":
                if abs(self.position[0] - x) < 10 and abs(self.position[1] - y) < 10:
                    print("freezer object found")
                    self.canmove = False
                    seconds_to_wait = Catalogue().attach(self.map.getid()).objects[id][4].d
                    # Create a new timer thread to wait for d seconds
                    timer = Thread(target=self.freeze, args=(seconds_to_wait,))
                    timer.start()
                    Catalogue().attach(self.map.getid()).removeObject(id)
                    Catalogue().attach(self.map.getid()).teammap(self.team.name).team_vision.pop(is_valid_uuid(id))

        return objectIter, teamIter, notify_all, image_path, x_discovered_until, y_discovered_until
            
    def mine(self, damage, bomb_x, bomb_y, proximity, bomb_id):
        sleep(5)
        # Check if anyone is in the proximity
        objectIter, teamIter, notify_all = Catalogue().attach(self.map.getid()).teammap(self.team.name).query(self.getid(),bomb_x, bomb_y, proximity)
        objectIter = list(objectIter)
        for qr in objectIter:
            id, name ,type , x, y = qr
            if type == "Player":
                Catalogue().attach(id).health -= damage
                print(f"{self.name}: Player {Catalogue().attach(id).username} got hurt")

        id = bomb_id
        Catalogue().attach(self.map.getid()).removeObject(id)
        Catalogue().attach(self.map.getid()).teammap(self.team.name).team_vision.pop(is_valid_uuid(id))
        self.activated_bombs.pop(id.hex)
        print(f"{self.name}: Mine exploded")
        # self.active = False

    
    def freeze(self, seconds_to_wait):
        sleep(seconds_to_wait)
        self.canmove = True
        print(f"{self.username}: Can move again")
    
    def drop(self, objecttype):
        for i in range(0, len(self.repo)):
            typename, *constructor_params = self.repo[i]
            if typename == objecttype:
                x = self.position[0]
                y = self.position[1]
                if typename == "Health":
                    if self.facing == 'N':
                        y = y - 5
                    elif self.facing == 'NE':
                        x = x + 3
                        y = y - 4
                    elif self.facing == 'E':
                        x = x + 5
                    elif self.facing == 'SE':
                        x = x + 3
                        y = y + 4
                    elif self.facing == 'S':
                        y = y + 5
                    elif self.facing == 'SW':
                        x = x - 3
                        y = y + 4
                    elif self.facing == 'W':
                        x = x - 5
                    elif self.facing == 'NW':
                        x = x - 3
                        y = y - 4
                # add object to the map, where repo[0] is the tuple of the object that contains the object type and constructor paramaters
                Catalogue().attach(self.map.getid()).addObject(f"{self.name}_{typename}",typename, x, y, *constructor_params)
                Catalogue().attach(self.map.getid()).teammap(self.team.name).addObject(f"{self.name}_{typename}",typename, x, y, *constructor_params)
                print(f"{self.username}: Dropped {typename}")
                self.repo.pop(i)
                break
        
        return None
