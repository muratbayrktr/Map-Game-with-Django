from map import Map
from utils.config import Config
from objects import *
from user import User, UserSwitcher

if __name__ == '__main__':
    # Create users
    UserManager = UserSwitcher()
    murat = User('muratbay61')
    arda = User('ardabak16')
    UserManager.add_user(murat)
    UserManager.add_user(arda)

    # Create map: map is loaded
    MAP = Map('test', (1024,1024), Config.load("test_map"))
    MAP.addObject('mine1', 'Mine', 10, 10, 1, 2, 3)
    MAP.addObject('health1', 'Health', 30, 30, 1, 2)
    MAP.addObject('freezer1', 'Freezer', 50, 50, 1, 2, 3)


    UserManager.switchuser(murat.user_id)
    print("USER SWITCHED:", UserManager.current_user.username, "User ID:", UserManager.current_user.user_id)
    murat_player = MAP.join(murat.username, 'RED')
    

    murat_player.move('S'); print("Murat position:",murat_player.position)
    murat_player.move('SE'); print("Murat position:",murat_player.position)
    murat_player.drop(Mine); print("Murat dropped.")
    print("Murat inventory:",murat_player.repo)
    objs = MAP.listObjects()
    print("Object List:")
    for obj in objs:
        if obj[1] == f"{UserManager.current_user.username}_Mine":
            pos = (obj[3], obj[4])
        print(obj)
    print("Murat's Mine position:",pos)


    UserManager.switchuser(arda.user_id)
    print("USER SWITCHED: ", UserManager.current_user.username, "User ID:", UserManager.current_user.user_id)
    arda_player = MAP.join(arda.username, 'RED')
    print("Arda inventory:",arda_player.repo)
    arda_player.move('E'); print("Arda position:",arda_player.position)
    arda_player.move('E'); print("Arda position:",arda_player.position)
    arda_player.drop(Health); print("Arda dropped.")
    print("Arda inventory:",arda_player.repo)
    objs = MAP.listObjects()
    print("Object List:")
    for obj in objs:
        if obj[1] == F"{UserManager.current_user.username}_Health":
            pos = (obj[3], obj[4])
        print(obj)
    print("Arda's Health position:",pos)



    