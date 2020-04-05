import json
import os

from storage import jsonencoder


class Objects:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        os.makedirs(os.path.join(self.path, "objects"), exist_ok=True)
        self.encoder = jsonencoder.Encoder()

    def save_object(self, object_name, object_instance):
        """Save object into json file"""
        with open(os.path.join(self.path, "objects", object_name + ".json"), "w") as file:
            json.dump(object_instance, file, cls=self.encoder.JSONEncoder)

    def load_object(self, object_name):
        """Load object from json file"""
        if self.save_exists(object_name):
            with open(os.path.join(self.path, "objects", object_name + ".json"), "r") as f:
                return json.load(f, object_hook=self.encoder.hook)

    def save_exists(self, object_name):
        """Check if json file exists"""
        return os.access(os.path.join(self.path, "objects", object_name + ".json"), os.R_OK | os.W_OK)
