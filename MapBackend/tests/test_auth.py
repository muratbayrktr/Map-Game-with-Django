import unittest
import os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from auth import Auth
from database import Database
from threading import Lock

class TestAuth(unittest.TestCase):
    dblock = Lock()
    def setUp(self):
        # Clear johnNo record 
        self.dblock.acquire()
        db = Database()
        db.execute("DELETE FROM users WHERE username='johnNO'")
        db.close()
        self.dblock.release()

    def test_signup_login(self):

        # Test case 1: Successful signup
        result = Auth.signup(self.dblock,"arda", "123")
        self.assertTrue(result)

        result = Auth.signup(self.dblock,"murat", "123")
        self.assertTrue(result)

        # Test case 2: Duplicate username
        result = Auth.signup(self.dblock,"arda", "456")
        self.assertFalse(result)
        

        # Test case 3: Successful login
        result = Auth.authenticate(self.dblock, "arda", "123")
        self.assertTrue(result)

        # Test case 4: Wrong password
        result = Auth.authenticate(self.dblock,"murat", "456")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

