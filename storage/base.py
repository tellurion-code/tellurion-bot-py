import json
import storage.jsonenc
from storage import path as pth


class Storage:
    """Basic class for storage interface

    All path are on unix format (`/folder1/folder2/file`)
    """

    def __init__(self):
        pass

    async def access(self, path):
        """
        Return if path is accessible
        :param path: Path to check
        :return: Boolean
        """
        pass

    async def chdir(self, path):
        """
        Change working directory for this storage module
        :param path: Path to go
        :return: New path
        """
        pass

    async def getcwd(self):
        """
        Get current working directory
        :return: Current working directory
        """
        pass

    async def listdir(self, path="."):
        """
        List all files and folders in directory `path`
        :param path: Folder to list
        :return: List of filename
        """
        pass

    async def mkdir(self, path):
        """
        Create directory `path`
        :param path: directory to create
        :return: Path to new directory
        """
        pass

    async def makedirs(self, path, exist_ok=False):
        """
        Create directory `path`
        :param exist_ok: Not return error if dir exists
        :param path: directory to create
        :return: Path to new directory
        """
        pass

    async def remove(self, path):
        """
        Remove file `path`
        :param path: File to remove
        :return: None
        """
        pass

    async def rename(self, src, dst):
        """
        Rename file `src` to `dst`
        :param src: Source file
        :param dst: Destination file
        :return: New path
        """
        pass

    async def rmdir(self, path):
        """
        Remove dir `path`
        :param path: Directory to remove
        :return: None
        """
        pass

    async def sync(self):
        """
        Force writing everything on disk (or storage support)
        :return: None
        """
        pass

    async def open(self, path, mode):
        """
        Return a file object
        :param path: Path of file
        :param mode: mode to open file
        :return: file object
        """
        pass

    async def exists(self, path):
        """
        Return if a file or a folder exists
        :param path: Path to test
        :return: True if file exists
        """
        pass

    async def isdir(self, path):
        """
        Return if path is a directory
        :param path: Path to test
        :return: True if path is a directory
        """
        pass


class Objects:
    storage: Storage

    def __init__(self, storage: Storage):
        self.storage = storage
        self.storage.makedirs("objects", exist_ok=True)

    async def save_object(self, object_name, object_instance):
        """Save object into json file"""
        with self.storage.open(pth.join("objects", object_name + ".json"), "w") as f:
            json.dump([object_instance], f, cls=storage.jsonenc.Encoder)

    async def load_object(self, object_name):
        """Load object from json file"""
        if await self.save_exists(object_name):
            with self.storage.open(pth.join("objects", object_name + ".json"), "r") as f:
                return json.load(f, object_hook=storage.jsonenc.hook)[0]

    async def save_exists(self, object_name):
        """Check if json file exists"""
        return self.storage.exists(pth.join("objects", object_name + ".json"))
