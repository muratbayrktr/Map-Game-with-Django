import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets')))
from map import Map
from objects import *
from utils.config import Config

class TestCatalogue(unittest.TestCase):
    def setUp(self):
        pass

    def test_getid(self):
        # Test the getid method
        # Create map object
        mine = Mine("mine1", (10, 10), 1, 2, 3)
        id = mine.getid()

        map = Map('test', (1024,1024), Config.load("test_map"))
        map.addObject('mine1', 'Mine', 10, 10, 1, 2, 3)
        idmap=map.getid()
        idobj = map.objects[list(map.objects.keys())[0]][4].getid()
        # Add map object to catalogue
        # Check that the id is correct
        self.assertEqual(id, mine.id)
        self.assertEqual(idmap, map.id)
        self.assertEqual(idobj,map.objects[list(map.objects.keys())[0]][4].id)


    def test_attach(self):
        # Test adding an item to the catalogue
        # Create map object
        mine = Mine("mine1", (10, 10), 1, 2, 3)
        # Add map object to catalogue
        id = mine.getid()
        self.assertEqual(Catalogue().attach(id), mine)


    def test_detach(self):
        # Test removing an item from the catalogue
        # Create map object
        mine = Mine("mine1", (10, 10), 1, 2, 3)
        # Add map object to catalogue
        id = mine.getid()
        Catalogue().detach(id)
        self.assertEqual(Catalogue().attach(id), None)

    def test_listobjects(self):
        # Test listing all objects in the catalogue
        # Create map object
        mine = Mine("mine1", (10, 10), 1, 2, 3)
        # Add map object to catalogue
        id = mine.getid()
        self.assertEqual(Catalogue().listobjects()[-1], (id, mine))

if __name__ == '__main__':
    unittest.main()

