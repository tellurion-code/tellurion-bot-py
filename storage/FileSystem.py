import os

from storage.base import Storage, Objects

class FSStorage(Storage):
    """
    Simple filesystem storage
    """

    def __init__(self, base_path="storage"):
        super().__init__()
        self.base_path = os.path.abspath(base_path)
        os.makedirs(self.base_path, exist_ok=True)
        self.current_dir = "/"

    def _topath(self, path):
        """Transform a path to a full path"""
        if path.startswith("/"):
            return os.path.join(self.base_path,  # Always add baspath to avoid going outside protected zone
                                os.path.abspath(os.path.join(self.base_path,
                                                             os.path.normpath(path))).lstrip(self.base_path))
        else:
            return os.path.join(self.base_path,  # Always add baspath to avoid going outside protected zone
                                os.path.abspath(os.path.join(self.base_path,
                                                             self.current_dir,
                                                             os.path.normpath(path))).lstrip(self.base_path))

    def access(self, path):
        # Normalize path and transform it to absolute path, remove base_path part and add it again to avoid going
        # outside protected folder
        return os.access(self._topath(path))

    def chdir(self, path):
        self.current_dir = self._topath(path)
        return self.current_dir

    def getcwd(self):
        return self.current_dir

    def listdir(self, path="."):
        return os.listdir(self._topath(path))

    def mkdir(self, path, exist_ok=False):
        if exist_ok:
            if self.exists(path):
                return self._topath(path)
        os.mkdir(self._topath(path))
        return self._topath(path)

    def makedirs(self, path, exist_ok=False):
        os.makedirs(self._topath(path), exist_ok=exist_ok)
        return self._topath(path)

    def remove(self, path):
        os.remove(self._topath(path))

    def rename(self, src, dst):
        os.rename(self._topath(src), self._topath(dst))
        return self._topath(dst)

    def rmdir(self, path):
        os.rmdir(self._topath(path))

    def sync(self):
        os.sync()

    def open(self, path, mode):
        return open(path, mode)

    def exists(self, path):
        return os.path.exists(path)

    def isdir(self, path):
        return os.path.isdir(self._topath(path))

class FSObjects(Objects):
    pass