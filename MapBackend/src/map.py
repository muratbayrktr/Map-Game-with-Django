from objects import *
from user import UserObserver
from PIL import Image
import sys
import os

class Map:
    ''' Constructor
    Creates a map with given dimensions
    (width,height) tuple as size. The background
    image is given as a file path in the config.    
    Background is blank if image is not provided
    '''
    def __init__(self, name:str, size:tuple, config:dict):
        self.name = name
        self.width, self.height = size
        self.config = config

        self.objects = {}
        self.players = {}
        self.teams = {}
        self.id = Catalogue()._instance.create_object(self, name, size, config)   

        # Blank image in the beginning
        self.background = Image.open(config.get("image"))
        # Initialize objects 
        for obj in config.get("objects"):
            x,y, objtype = obj
            self.addObject(objtype, objtype, x, y)



    def __del__(self):
        '''Destructor'''
        try:
            self.background.close()
        except:
            pass

    def getid(self):
        '''Returns the id of the map'''
        return self.id
        
    def addObject(self, name, type, x,y, *args, **kwargs) -> None:  
        '''Adds an object on the 2D grid. type is explained below'''   
        newObject = ObjectFactory.createObject(name, type, (x, y), *args, **kwargs) 
        self.objects[newObject.getid()] = (name, type, x, y, newObject) 
        
    def removeObject(self, id) -> None:
        '''Remove the object with id.'''
        self.objects.pop(id)

    def listObjects(self) -> iter: # the id part ??
        '''return all objects in the map with (id, name, type, x, y) tuple as an iterator'''
        objectList = []
        for key,value in self.objects.items():
            # append ((id, name, type, x, y))
            objectList.append((key, value[0], value[1], value[2], value[3]))
        return iter(objectList)

    def getImage(self, x, y, r) -> Image:
        '''get the background image defined by the rectangle. 
        Rectangle is defined as a 2*r by 2*r square centered at x,y'''
        im = Image.open(self.config.get("image")).crop((x-r if x-r > 0 else 0, y-r if y-r > 0 else 0, x+r, y+r))
        return im

    def setImage(self, x, y, r, image) -> None:
        '''set the background image patch at the rectangle.'''
        self.background.paste(image, (x-r if x-r > 0 else 0, y-r if y-r > 0 else 0, x+r, y+r))

    def query(self, x, y, r) -> iter:
        '''return all objects in a rectangular area as an iterator. 
        Area is defined as a 2*r by 2*r square centered at x,y'''
        objects_in_area = []
        # value = (name, type, x, y, newObject) 
        for key,value in self.objects.items():
            if value[2] >= x-r and value[2] <= x+r and value[3] >= y-r and value[3] <= y+r:
                objects_in_area.append((key, value[0], value[1], value[2], value[3]))
        for key,value in self.players.items():
            player = Catalogue().attach(value.getid())
            if player.position[0] >= x-r and player.position[0] <= x+r and player.position[1] >= y-r and player.position[1] <= y+r:
                objects_in_area.append((player.getid(), player.name, "Player", player.position[0], player.position[1]))

        return iter(objects_in_area)

    def join(self, playerName:str, teamName:str):
        '''A player joins the game of the global map. team is a 
        string for the team name. If team name exists, user is 
        associated with the Map of the team, otherwise the Map is created.'''
        if teamName in self.teams:
            self.teams[teamName].join(playerName, teamName)
        else:
            self.teams[teamName] = TeamMap(teamName, (self.width, self.height), self.config,self)
            self.teams[teamName].join(playerName, teamName)
        self.players[playerName] = self.teams[teamName].team_players[playerName]
        return self.teams[teamName].team_players[playerName]

    def leave(self, player, team):
        '''A player leaves the game. Users have to call join() before 
        leaving the map and leave() existing games before joining again.'''
        if team in self.teams:
            self.teams[team].leave(player)
            self.players.pop(player)
        else:
            raise Exception("Team does not exist")
    
    def teammap(self, team):
        '''Returns the team map of the given team name'''
        return self.teams[team]



class TeamMap(Map):
    '''Constructor
    Creates a team map with given dimensions
    (width,height) tuple as size. The background
    image is given as a file path in the config.    
    Background is blank if image is not provided
    '''
    def __init__(self, name:str, size:tuple, config:dict, supermap:Map):
        super().__init__(name, size, config)
        self.team_players = {}
        self.team_vision = {}
        self.config = config
        self.x_discovered_until = config.get("playervision")
        self.y_discovered_until = config.get("playervision")
        self.supermap = supermap
        self.background.close()
        self.background = Image.new('RGB', (self.width, self.height), (0, 0, 0))

    def __del__(self):
        '''Destructor'''
        try:
            self.background.close()
        except:
            pass

    def query(self, player_id, x, y, r) -> iter:
        # print("here")
        super_query = Catalogue().attach(self.supermap.getid()).query(x, y, r)
        super_query_list = list(super_query)
        notify_all = False
        for qr in super_query_list:
            id, name ,type , x, y = qr
            # if id == player_id:
            #     continue
            if id in self.team_vision:
                if (name, type, x, y) != self.team_vision[id]:
                    self.team_vision[id] = (name, type, x, y)
                    notify_all = True
            else:
                notify_all = True
                self.team_vision[id] = (name, type, x, y)

        return_query_list = []
        # Create a an iter object from the self.team_vision dictionary
        for key,value in self.team_vision.items():
            # append ((id, name, type, x, y))
            return_query_list.append((key, value[0], value[1], value[2], value[3]))

        # pop the player from the list
        # for i in range(0, len(super_query_list)):
        #     if super_query_list[i][0] == player_id:
        #         super_query_list.pop(i)
        #         break

        return iter(super_query_list), iter(return_query_list), notify_all

    def join(self, playerName:str, teamName:str):
        '''A player joins the game of the team map. team is a 
        string for the team name. If team name exists, user is 
        associated with the Map of the team, otherwise the Map is created.'''
        # Player(user, team, health, repo, map)
        health = self.config.get("playerh")
        repo = self.config.get("playerrepo").copy()
        player = Player(playerName, self, health, repo, self.supermap)
        self.team_players[playerName] = player
        remid = None
        for key,value in self.team_vision.items():
            if value[0] == playerName:
                remid = key

        if remid is not None:
            self.team_vision.pop(remid)

    def leave(self, player):
        '''A player leaves the game. Users have to call join() before 
        leaving the map and leave() existing games before joining again.'''
        self.team_players.pop(player)
        
        