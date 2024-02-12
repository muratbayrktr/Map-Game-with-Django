import os
import json

class Config:
    def __init__(self,filename):
        self.data = self.load(filename=filename)

    @staticmethod
    def load(filename):
        data = {}
        file = os.path.join("assets","maps", f"{filename}.json")
        if os.path.exists(file):
            with open(file) as f:
                data = json.load(f)
                
        return data

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value