from test_catalogue import TestCatalogue
from test_map import TestMap
from test_player import TestPlayer
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets')))
from map import Map
from objects import *
from utils.config import Config
from objects import Catalogue

if __name__ == '__main__':
    unittest.main()
