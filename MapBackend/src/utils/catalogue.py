import uuid
import pickle
import os

class Catalogue:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Catalogue, cls).__new__(cls)
            cls._instance.objects = {}
        return cls._instance

    def create_object(self, obj, *args, **kwargs):
        obj_id = uuid.uuid4()  # Generates a unique identifier
        self.objects[obj_id] = obj
        return obj_id

    def attach(self, obj_id):
        return self.objects.get(obj_id)

    def detach(self, obj_id):
        if obj_id in self.objects:
            del self.objects[obj_id]

    def save(self, obj_id):
        if obj_id in self.objects:
            obj = self.objects[obj_id]
            with open(f'instances/{obj_id}.pkl', 'wb') as file:
                pickle.dump(obj, file)
        else:
            raise ValueError("Object ID not found in Catalogue")

    def load(self, obj_id):
        try:
            with open(f'instances/{obj_id}.pkl', 'rb') as file:
                obj = pickle.load(file)
            self.objects[obj_id] = obj
            return obj
        except FileNotFoundError:
            raise ValueError("File for the given Object ID not found")
        
    def dump(self):
        for obj_id, obj in self.objects.items():
            with open(f'instances/{obj_id}.pkl', 'wb') as file:
                pickle.dump(obj, file)

    def loadall(self):
        for file in os.listdir('instances'):
            obj_id = uuid.UUID(file[:-4])
            self.load(obj_id)


    @classmethod
    def listobjects(cls):
        return [(obj_id, obj) for obj_id, obj in cls._instance.objects.items()]
