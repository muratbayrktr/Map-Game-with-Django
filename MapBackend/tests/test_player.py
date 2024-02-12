import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets')))
from map import Map
from objects import *
from utils.config import Config


class TestPlayer(unittest.TestCase):
    def setUp(self):
        config = Config.load("test_map")
        self.width = 1024
        self.height = 1024
        self.map = Map('test', (self.width,self.height), config)


    def test_init(self):
        player = Player('test', 'test', 100, 'test', self.map)
        oid = Catalogue().listobjects()[-1]
        self.assertEqual(player.id, oid[0])
        self.assertEqual(player, oid[1])

    def test_move(self):
        self.map.join('test', 'test')
        self.map.addObject('mine1', 'Mine', 4, 4, 1, 2, 3)
        player = Catalogue().attach(self.map.players['test'].getid())
        impix= player.map.background.getpixel((0,1))
        objiter = player.move("S")
        # Check position
        self.assertEqual(player.position, (0,1))
        # Check object iterator
        self.assertEqual(list(objiter), list(player.map.query(0,1,player.playervision)))
        # Check if team map image has been set
        self.assertEqual(impix, player.team.background.getpixel((0,1)))

    def test_drop(self):
        self.map.join('test', 'test')
        player = Catalogue().attach(self.map.players['test'].getid())
        player.drop(Mine)
        oids = Catalogue().listobjects()
        id = None
        for i in range(0, len(oids)):
            if oids[i][1].name == f'{player.username}_Mine':
                id = oids[i][0]
                break
        print(player.map.objects)
        # Check if the object is dropped
        self.assertEqual(player.map.objects[id][2], player.position[0])
        self.assertEqual(player.map.objects[id][3], player.position[1])
        # Check if the object is removed from the repo
        self.assertEqual(len(player.repo), 2)


if __name__ == "__main__":
    unittest.main()