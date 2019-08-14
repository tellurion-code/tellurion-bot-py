import os

import yaml

from config.Base import Config


class FSConfig(Config):
    path: str

    def __init__(self, path="config.json", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "a").close()

    def _load(self):
        with open(self.path, "r") as file:
            content = file.read()
        self.config = yaml.load(content, Loader=yaml.BaseLoader)
        if self.config is None:
            self.parent.config[self.name] = {}
            self.config = {}

    def _save(self):
        content = yaml.dump(self.config)
        print(self.config)
        with open(self.path, "w") as file:
            file.write(content)
