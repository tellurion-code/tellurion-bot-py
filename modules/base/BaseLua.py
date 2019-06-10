"""Base class for module, never use directly !!!"""
import asyncio
import os
import sys
import pickle
import traceback

import discord
import lupa

from modules.base.Base import BaseClass
from storage import FSStorage
import storage.path as path


class BaseClassLua(BaseClass):
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

    def __init__(self, client, path):
        """Initialize module class

        Initialize module class, always call it to set self.client when you override it.

        :param client: client instance
        :type client: NikolaTesla"""
        super().__init__(client)
        # Get lua globals
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        print(os.path.abspath(path))
        self.luaMethods = self.lua.require(path)

    def dispatch(self, event, *args, **kwargs):
        method = "on_"+event
        if self.luaMethods[method] is not None:
            self.luaMethods[method](asyncio.ensure_future, self, *args, **kwargs)
        else: # If lua methods not found, dispatch to python methods
            super().dispatch(event, *args, **kwargs)

    async def _run_event(self, coro, event_name, *args, **kwargs):
        # Overide here to execute lua on_error if it exists
        # Run event
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            # If function is cancelled pass silently
            pass
        except Exception:
            try:
                # Call error function
                if self.luaMethods["on_error"] is not None:
                    self.luaMethods["on_error"](self, asyncio.ensure_future, discord, *args, **kwargs)
                else:
                    await self.on_error(event_name, *args, **kwargs)
            except asyncio.CancelledError:
                # If error event is canceled pass silently
                pass

    async def on_error(self, event_method, *args, **kwargs):
        # Base on_error event, executed if lua not provide it
        # Basic error handler
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()

