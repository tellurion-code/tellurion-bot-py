import os
from aiofile import AIOFile, Reader, Writer
import yaml

from config.Base import Config


class FSConfig(Config):
    def __init__(self, path="config.json", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "a").close()

    async def _load(self):
        content = ""
        async with AIOFile(self.path, "r") as afp:
            reader = Reader(afp, chunk_size=8)
            async for chunk in reader:
                content+=chunk
        self.config = yaml.load(content, Loader=yaml.BaseLoader)

    async def _save(self):
        content = yaml.dump(self.config)
        async with AIOFile(self.path, "w") as afp:
            writer = Writer(afp)
            await writer(content)
            await afp.fsync()