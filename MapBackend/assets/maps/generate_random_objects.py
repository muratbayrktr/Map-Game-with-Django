import os
import json
import random

folder_path = "/Users/muratbayrktr/Desktop/Ceng/CENG445 Scripting/phase3/MapBackend/assets/maps"
categories = ["Mine", "Health", "Freezer"]
num_objects = 50

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r+") as file:
            data = json.load(file)
            # objects = data.get("objects", [])
            objects = []
            
            for _ in range(num_objects):
                category = random.choice(categories)
                # object_data format example is [5,5,"Mine"]
                object_data = [random.randint(0, 1024), random.randint(0, 1024), category]
                objects.append(object_data)
            
            data["objects"] = objects
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
