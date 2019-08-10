import asyncio


class Config:
    def __init__(self, config: dict = None, parent = None, name: str = None):
        if config is None:
            config = {}
        self.config = config
        self.parent = parent
        self.cache = []
        if self.parent:
            self.parent = parent
            self.name = name
            self.parent.config[self.name] = self.config

    async def _save(self):
        if self.parent:
            self.parent.save()

    def save(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self._save(), loop=loop)

    async def _load(self):
        if self.parent:
            self.parent.load()
            self.config = self.parent.config[self.name]

    def load(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self._load(), loop=loop)

    def __getitem__(self, item):
        return self.config.get(item)

    def __setitem__(self, key, value):
        if self.parent:
            self.parent[self.name][key] = value
            self.config = self.parent[self.name]
        else:
            self.config[key] = value
        self.save()