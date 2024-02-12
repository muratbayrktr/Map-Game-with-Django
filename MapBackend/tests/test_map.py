import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets')))
from map import Map
from utils.config import Config
from objects import Catalogue

class TestMap(unittest.TestCase):
    def setUp(self):
        config = Config.load("test_map")
        self.width = 1024
        self.height = 1024
        self.map = Map('test', (self.width,self.height), config)

    def test_init(self):
        self.assertEqual(self.map.name, 'test')
        self.assertEqual(self.map.width, self.width)
        self.assertEqual(self.map.height, self.height)
        self.assertEqual(self.map.objects, {})
        self.assertEqual(self.map.config, Config.load("test_map"))
        self.assertEqual(self.map.id, self.map.getid())

    def test_addObject(self):
        # Mine takes extra 3 parameters p, d, k
        self.map.addObject('mine1', 'Mine', 10, 10, 1, 2, 3)
        # Health takes extra 1 parameter inf
        self.map.addObject('health1', 'Health', 10, 10, 1,2)
        # Freezer takes extra 3 parameters p, d, k
        self.map.addObject('freezer1', 'Freezer', 10, 10, 1, 2, 3)
        # self.map.listObjects() returns an iterator of tuples
        oids = Catalogue().listobjects()
        for key, value in self.map.objects.items():
            self.assertEqual(Catalogue().attach(key), self.map.objects[key][4])


    def test_removeObject(self):
        # Test all the object types are removed correctly
        # Mine takes extra 3 parameters p, d, k
        self.map.addObject('mine1', 'Mine', 10, 10, 1, 2, 3)
        # Health takes extra 1 parameter inf
        self.map.addObject('health1', 'Health', 10, 10, 1,2)
        # Freezer takes extra 3 parameters p, d, k
        self.map.addObject('freezer1', 'Freezer', 10, 10, 1, 2, 3)
        # self.map.listObjects() returns an iterator of tuples
        oids = list(self.map.objects.keys())
        self.map.removeObject(oids[0])
        self.map.removeObject(oids[1])
        self.map.removeObject(oids[2])

        self.assertEqual(list(self.map.objects.values()), [])


    def test_listObjects(self):
        # Test all the object types are listed correctly
        # Mine takes extra 3 parameters p, d, k
        self.map.addObject('mine1', 'Mine', 10, 10, 1, 2, 3)
        # Health takes extra 1 parameter inf
        self.map.addObject('health1', 'Health', 10, 10, 1,2)
        # Freezer takes extra 3 parameters p, d, k
        self.map.addObject('freezer1', 'Freezer', 10, 10, 1, 2, 3)
        oids = Catalogue().listobjects()

        self.assertEqual(list(self.map.listObjects())[0], (oids[-3][0],'mine1', 'Mine', 10, 10))
        self.assertEqual(list(self.map.listObjects())[1], (oids[-2][0],'health1', 'Health', 10, 10))
        self.assertEqual(list(self.map.listObjects())[2], (oids[-1][0],'freezer1', 'Freezer', 10, 10))
        
    def test_getImage(self):
        # Test the image is cropped correctly
        # Test the image is blank if no image is provided
        self.assertEqual(self.map.getImage(10, 10, 10).size, (20, 20))
        self.assertEqual(self.map.getImage(10, 10, 10).getpixel((0,0)), (35, 31, 20))

    def test_setImage(self):
        # Test the image is pasted correctly
        # Test the image is blank if no image is provided
        self.map.setImage(10, 10, 10, self.map.getImage(10, 10, 10))
        self.assertEqual(self.map.background.getpixel((10,10)), (38, 30, 7))

    def test_query(self):
        # Test all the object types are queried correctly
        # Mine takes extra 3 parameters p, d, k
        self.map.addObject('mine1', 'Mine', 11, 11, 1, 2, 3)
        # Health takes extra 1 parameter inf
        self.map.addObject('health1', 'Health', 9, 9, 1,2)
        # Freezer takes extra 3 parameters p, d, k
        self.map.addObject('freezer1', 'Freezer', 9, 12, 1, 2, 3)
        oids = Catalogue().listobjects()
        self.assertEqual(list(self.map.query(10, 10, 10))[0], (oids[-3][0],'mine1', 'Mine', 11, 11))
        self.assertEqual(list(self.map.query(10, 10, 10))[1], (oids[-2][0],'health1', 'Health', 9, 9))
        self.assertEqual(list(self.map.query(10, 10, 10))[2], (oids[-1][0],'freezer1', 'Freezer', 9, 12))

    def test_join(self):
        self.map.join('testPlayer', 'testTeam')
        self.assertEqual(self.map.players['testPlayer'].username, 'testPlayer')

    def test_leave(self):
        self.map.join('testPlayer', 'testTeam')
        self.map.leave('testPlayer', 'testTeam')
        self.assertEqual(self.map.players, {})

    def test_teammap(self):
        self.map.join('testPlayer', 'testTeam')
        teammap = self.map.players['testPlayer'].team
        self.assertEqual(self.map.teammap('testTeam'), teammap)

if __name__ == '__main__':
    unittest.main()