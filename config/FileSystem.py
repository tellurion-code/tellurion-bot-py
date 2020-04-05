import os

import toml

from config.Base import Config


class FSConfig(Config):
    path: str

    def __init__(self, path="config.toml", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "a").close()

    def _load(self):
        with open(self.path, "r") as file:
            content = file.read()
        self.config = toml.loads(content)
        if self.config is None:
            self.config = {}

    def _save(self):
        content = toml.dumps(self.config)
        with open(self.path, "w") as file:
            file.write(content)
