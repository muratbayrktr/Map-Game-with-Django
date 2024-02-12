
import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        if os.path.exists("database.db"):
            os.remove("database.db")
        self.db = Database()

    def tearDown(self):
        self.db.close()

    def test_connect(self):
        self.db.connect()
        self.assertTrue(self.db.is_connected)

    def test_execute(self):
        self.db.connect()
        query = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)"
        self.db.execute(query)
        result = self.db.fetch_all("SELECT username FROM users")
        self.assertEqual(len(result), 0)
        self.db

    def test_fetch_all(self):
        self.db.connect()
        query = "INSERT INTO users (username, password) VALUES (?,?)"
        params = ("John","123")
        self.db.execute(query, params)
        result = self.db.fetch_all("SELECT username FROM users")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "John")

    def test_fetch_one(self):
        self.db.connect()
        query = "INSERT INTO users (username,password) VALUES (?,?)"
        params = ("Jane","123")
        self.db.execute(query, params)
        result = self.db.fetch_one("SELECT username FROM users WHERE username=?", ("Jane",))
        self.assertEqual(result[0], "Jane")

        # Clean up the database
        query = "DELETE FROM users WHERE username=?"
        self.db.execute(query, ("Jane",))

if __name__ == '__main__':
    unittest.main()

