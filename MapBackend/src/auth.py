import hashlib
import sqlite3
from database import Database


class Auth:
    dbname = "database.db"
    @staticmethod
    def authenticate(lock, user,passwd):
        try:
            query = 'SELECT username,password FROM users WHERE username=?'
            params = (user,)
            lock.acquire()
            with sqlite3.connect(Auth.dbname) as db:
                c = db.cursor()
                row = c.execute(query,params)
                row = row.fetchone()
                if hashlib.sha256(passwd.encode()).hexdigest() == row[1]:
                    return True
        except sqlite3.IntegrityError:
            print("Username already exists")
            return False
        except TypeError:
            print("Wrong number of arguments")
        except IndexError:
            print("No such user")
        except Exception as e:
            print(e)
        finally:
            lock.release()
        return False
    
    @staticmethod
    def auth_with_token(token):
        return True

    @staticmethod
    def signup(lock, user,passwd):

        try:
            encpass = hashlib.sha256(passwd.encode()).hexdigest()  
            query = 'INSERT INTO users (username, password) VALUES (?,?)'
            params = (user,encpass)
            lock.acquire()
            with sqlite3.connect(Auth.dbname) as db:
                c = db.cursor()
                c.execute(query,params)
                db.commit()
        except sqlite3.IntegrityError:
            print("Username already exists")
            return False
        except Exception as e:
            print(e)
            return False
        finally: 
            lock.release()
        return True
    
    @staticmethod
    def success():
        return True
    
    @staticmethod
    def failiure():
        return False
    
    

