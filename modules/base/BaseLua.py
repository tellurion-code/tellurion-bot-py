"""Base class for module, never use directly !!!"""
import asyncio
import sys
import pickle
import traceback

import discord
import lupa

from storage import FSStorage
import storage.path as path


class BaseClassLua:
    """Base class for all modules, Override it to make submodules"""
    name = ""
    help = {
        "description": "",
        "commands": {

        }
    }
    help_active = False
    color = 0x000000
    command_text = None
    super_users = []
    authorized_roles = []

    def __init__(self, client):
        """Initialize module class

        Initialize module class, always call it to set self.client when you override it.

        :param client: client instance
        :type client: NikolaTesla"""
        self.client = client
        self.storage = FSStorage(path.join(self.client.base_path, self.name))
        if not self.storage.isdir(path.join("storage", self.name)):
            self.storage.makedirs(path.join("storage", self.name), exist_ok=True)
        # Get lua globals
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self.luaMethods = self.lua.eval("require \"main\"")

    def dispatch(self, event, *args, **kwargs):
        print(self.luaMethods)
        print(self.luaMethods.__dict__)
        print(dict(self.luaMethods))

