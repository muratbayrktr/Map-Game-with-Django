

import sys
import os
from socket import *
import random
import asyncio
import websockets
import logging
import json
import http.cookies
from threading import Thread
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

## Uncomment following to use session_keys from django.
## This way request authentication will be
## achieved. similarly CSRF token can be used for
## authentication as well.

#import django
#from django.contrib.session.models import Session
#
#def setupDjango(projectpath, projectname):
#	'''call this once to setup django environment'''
#	sys.path.append(projectpath)
#	os.environ.setdefault('DJANGO_SETTINGS_MODULE',projectname + '.settings')
#	django.setup()
#
#def checksession(sessionkey):
#	'''check UDP/WS supplied id againts django session keys
#	   for browser, 'sessionid' cookie will save this id
#	   for django view request.session.session_key gives this id.
#		simply view sends udp notifications with request.session.session_key and
#		browser sends sessionid cookie. Note that they don't need to match.
#		User A can send notification to user B. But both have session ids.
#	'''
#	try:
#		Session.objects.get(session_key=sessionkey)
#		return True
#	except:	
#		return False
def singleton(cls):
        '''generic python decorator to make any class
        singleton.'''
        _instances = {}   # keep classname vs. instance
        def getinstance():
                '''if cls is not in _instances create it
                and store. return the stored instance'''
                if cls not in _instances:
                        _instances[cls] = cls()
                return _instances[cls]
        return getinstance



@singleton
class Notifications:
	'''An observer class, saving notifications and notifiying
		registered coroutines'''
	def __init__(self):
		self.observers = {}
		self.broadcast = set()
		self.messages = {}

	def newconnection(self, ws):
		self.broadcast.add(ws)

	def closeconnection(self, ws):
		self.broadcast.discard(ws)

	def register(self, ws, cid):
		'''register a Lock and an id string'''
		if cid in self.observers:
			self.observers[cid].add(ws)
		else:
			self.observers[cid] = set([ws])
		print('Current observers',self.observers,self.broadcast)

	def unregister(self, ws, cid):
		'''remove registration'''
		if cid not in self.observers:
			return
		self.observers[cid].discard(ws)
		if self.observers[cid] == set():
			del self.observers[cid]
		print('Current observers',self.observers,self.broadcast)

	async def addNotification(self, oid, message):
		'''add a notification for websocket conns with id == oid
			the '*' oid is broadcast. Message is the dictionary
			to be sent to connected websockets.
		'''
		print(oid, message)
		if oid == '*':     # broadcast message
			for c in self.broadcast:
				await c.send(json.dumps(message))
		elif oid in self.observers:
			for c in self.observers[oid]:
				await c.send(json.dumps(message))


		
async def websockethandler(websocket, path):
	
	# websocket.request_headers is a dictionary like object
	print (websocket.request_headers.items())
	# following parses the cookie object
	if 'Cookie' in websocket.request_headers:
		print(http.cookies.SimpleCookie(websocket.request_headers['Cookie']))

	# get the list of ids to follow from browser
	reqlist = await websocket.recv()
	idlist = json.loads(reqlist)
	
	print('connected', idlist)

	Notifications().newconnection(websocket)
	if type(idlist) != list:
		idlist = [idlist]
	for myid in idlist:
		Notifications().register(websocket, myid)
	idlist = set(idlist)

	try:
		while True:
			data = await websocket.recv()
			try:
				message = json.loads(data)
				if "command" in message:
					# print(message["command"])
					pass
				
				if "command" in message and message['command'] == 'listmaps':
					MESS = {}
					MESS["command"] = "listmaps"
					objs = Catalogue.listobjects()
					maps = []
					for id,obj in objs:
						# Filter maps
						if isinstance(obj, Map) and not isinstance(obj, TeamMap): 
							# print(obj.name) 
							teams = [x for x in obj.teams.keys()] if obj.teams != {} else []
							if teams == []:
								maps.append({"name":obj.name,"id":id.hex,"teams":[]})
							else:
								maps.append({"name":obj.name,"teams":teams,"id":id.hex})

					MESS["maps"] = maps
					print("sending", MESS)
					await websocket.send(json.dumps(MESS))
				elif "command" in message and message['command'] == 'join':
					print("Joining map", message["mapid"], "with team", message["team"], "and name", message["username"])
					mapid = is_valid_uuid(message["mapid"])
					GMAP = Catalogue().attach(mapid)
					player = GMAP.join(message["username"], message["team"])
					player_uuid = player.getid()
					MESS = {}
					MESS["command"] = "setId"
					MESS["player_id"] = player_uuid.hex
					MESS["map_id"] = GMAP.getid().hex
					await websocket.send(json.dumps(MESS))

					
					x,y = player.position
					Catalogue().attach(GMAP.getid()).teammap(player.team.name).setImage(x, y, player.playervision, Catalogue().attach(GMAP.getid()).getImage(x, y, player.playervision))

					# Get image
					image = Catalogue().attach(GMAP.getid()).teammap(player.team.name).background
					image.save("test.png")

					MESS = {}
					MESS["command"] = "updateMap"
					# Broadcast the update to all players in the team
					MESS["id"] = "*"
					await Notifications().addNotification(MESS['id'], MESS)
				elif "command" in message and message['command'] == 'newmap':
					print("Creating new map", message["mapname"], "with size", message["mapwidth"], message["mapheight"])
					name = message["mapname"]
					print(name)
					width = int(message["mapwidth"])
					print(width)
					height = int(message["mapheight"])
					print(height)
					GMAP = Map(name, (width,height), Config.load(name))
					print(GMAP.getid())
					Catalogue().save(GMAP.getid())
					
					# Update view
					MESS = {}
					MESS["command"] = "listmaps"
					objs = Catalogue.listobjects()
					maps = []
					for id,obj in objs:
						# Filter maps
						if isinstance(obj, Map) and not isinstance(obj, TeamMap): 
							# print(obj.name) 
							teams = [x for x in obj.teams.keys()] if obj.teams != {} else []
							if teams == []:
								maps.append({"name":obj.name,"id":id.hex,"teams":[]})
							else:
								maps.append({"name":obj.name,"teams":teams,"id":id.hex})

					MESS["maps"] = maps
					print("sending", MESS)
					await websocket.send(json.dumps(MESS))

				elif "command" in message and message['command'] == 'updateMap':
					map_uuid = is_valid_uuid(message["map_uuid"])
					player_uuid = is_valid_uuid(message["player_uuid"])
					player_teamname = Catalogue().attach(player_uuid).team.name
					image = Catalogue().attach(map_uuid).teammap(player_teamname).background
					x,y, = Catalogue().attach(player_uuid).position
					playervision = Catalogue().attach(player_uuid).playervision
					objectIter, teamIter, notify_all = Catalogue().attach(map_uuid).teammap(player_teamname).query(player_uuid,x, y, playervision)

					self_query = list(objectIter)
					team_query = list(teamIter)

					def merge_team_with_player_vision(self_query, team_query):
						# Merges two lists of tuples into one list of tuples
						# If there is a tuple with the same id in both lists, the tuple in the self_query will be used
						# If there is a tuple with the same id in only one list, that tuple will be used
						for team_tuple in team_query:
							if team_tuple[0] not in [x[0] for x in self_query]:
								self_query.append(team_tuple)
						return self_query
					
					merged_query = merge_team_with_player_vision(self_query, team_query)
					buffered = io.BytesIO()
					image.save(buffered, "PNG")
					MESS = {}
					MESS["command"] = "loadMap"
					MESS["image"] =  base64.b64encode(buffered.getvalue()).decode('ascii')
					MESS["query"] = [[x.hex if isinstance(x, uuid.UUID) else x for x in y] for y in merged_query]
					# print(MESS)
					await websocket.send(json.dumps(MESS))
				elif "command" in message and message['command'] == 'leave':
					player_uuid = is_valid_uuid(message["player_uuid"])
					map_uuid = is_valid_uuid(message["map_uuid"])
					playername = Catalogue().attach(player_uuid).name
					Catalogue().attach(map_uuid).teammap(Catalogue().attach(player_uuid).team.name).team_vision.pop(player_uuid.hex)
					try:
						Catalogue().attach(map_uuid).leave(playername, Catalogue().attach(player_uuid).team.name)
					except Exception as e:
						print(e)
						raise Exception("Team does not exist")
					MESS = {}
					MESS["command"] = "updateMap"
					# Broadcast the update to all players in the team
					MESS["id"] = "*"
					await Notifications().addNotification("*", MESS)
				elif "command" in message and message['command'] == 'move':
					direction = message["direction"]
					player_uuid = is_valid_uuid(message["player_uuid"])
					map_uuid = is_valid_uuid(message["map_uuid"])
					Catalogue().attach(player_uuid).move(direction)
					MESS = {}
					MESS["command"] = "updateMap"
					# Broadcast the update to all players in the team
					MESS["id"] = "*"
					await Notifications().addNotification("*", MESS)
				elif "command" in message and message['command'] == 'drop':
					player_uuid = is_valid_uuid(message["player_uuid"])
					map_uuid = is_valid_uuid(message["map_uuid"])
					
					randchoice = ["Health", "Mine", "Freezer"]
					randint = random.randint(0,2)
					Catalogue().attach(player_uuid).drop(randchoice[randint])
					MESS = {}
					MESS["command"] = "updateMap"
					# Broadcast the update to all players in the team
					MESS["id"] = "*"
					await Notifications().addNotification("*", MESS)
				elif "command" in message and message['command'] == 'add':
					Notifications().register(websocket, message['id'])
					idlist.add(message['id'])
				elif "command" in message and message['command'] == 'delete': 
					Notifications().unregister(websocket, message['id'])
					idlist.discard(message['id'])
				else:
					await Notifications().addNotification(message['id'], message) 
			except Exception as e:
				print("invalid message. {} : exception: {}".format(data, str(e)))
			finally:
				Catalogue().dump()
	except Exception as e:
		print(e)
	finally:
		print('closing', idlist)
		for myid in idlist:
			Notifications().unregister(websocket, myid)
		Notifications().closeconnection(websocket)
		websocket.close()

Catalogue().loadall()

# Catalogue().listobjects()
try:
	print(Catalogue.listobjects())
except Exception as e:
	print(e)
	print("No objects loaded")

#enable logging
# logging.basicConfig(level=logging.DEBUG)

try:
	ws_addr = sys.argv[1].split(':',1)
	if ws_addr[0] == '' : ws_addr[0] = '0'
	ws_addr = getaddrinfo(ws_addr[0], ws_addr[1], AF_INET, SOCK_STREAM)
	ws_addr = ws_addr[0][4]
except Exception as e:
	sys.stderr.write("{}\nusage: {} wsip:port\n".format(e, sys.argv[0]))
	sys.exit()



# following creates a websocket handler
loop = asyncio.get_event_loop()
loop.set_debug(True)
ws_server = websockets.serve(websockethandler, ws_addr[0], ws_addr[1], loop = loop)

#loop.run_until_complete(ws_server)
# start both in an infinite service loop
#asyncio.async(ws_server)
#asyncio.ensure_future(ws_server)
loop.run_until_complete(ws_server)
loop.run_forever()

