from utils.catalogue import Catalogue

class User:
    def __init__(self, username):
        self.user_id = Catalogue()._instance.create_object(self)
        self.username = username
        self.observers = []  # List of observers to be notified on switch

    def attach_observer(self, observer):
        self.observers.append(observer)

    def detach_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

    def switch_to_user(self):
        self.notify_observers()

    def __str__(self):
        return f"User({self.username})"

class UserObserver:
    def update(self, user):
        raise NotImplementedError("Subclass must implement this method")


class UserSwitcher:
    def __init__(self):
        self.current_user = None
        self.users = {}

    def add_user(self, user):
        self.users[user.user_id] = user

    def switchuser(self, user_id):
        if user_id in self.users:
            self.current_user = self.users[user_id]
            self.current_user.switch_to_user()
        else:
            print("User ID does not exist.")

