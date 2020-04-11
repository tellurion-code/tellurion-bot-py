from __future__ import annotations

from typing import Dict, Any, Optional


class Config:
    name: Optional[str]
    parent: Optional[Config]
    config: Dict[Any, Any]

    def __init__(self, parent: Config = None, name: str = None, client: LBI = None):
        """Create Config

        :param parent: Parent configuration
        :param name: Configuration name
        :type parent: Config
        :type name: str"""
        self.parent = parent
        self.config = dict()
        self.name = None
        self.client = client
        if self.parent:
            self.name = name
            self.client = self.parent.client

    def init(self, config):
        """Load default configuration

        :param config: Default configuration
        :type config: dict
        :return: None"""
        # Load data from config file before initialisation
        self.load()
        # Get data from parent
        if self.parent is not None:
            self.parent.config[self.name] = self.parent.config.get(self.name) if self.parent.config.get(
                self.name) is not None else self.config
            self.config = self.parent.config[self.name]
        # Set config only if not already defined
        for k, v in config.items():
            self.config[k] = self.config.get(k) if self.config.get(k) is not None else v
        # Save new datas
        self.save()

    def _save(self):
        """Internal function for save

        Must be overridden by all type of config to handle saving"""
        # Call parent save if necessary
        if self.parent:
            self.parent.save()

    def save(self):
        """Public save function

        Do not override"""
        self._save()

    def _load(self):
        """Internal function for load

        Mus be overridden by all type of config to handle loading"""
        # Load parent if necessary
        if self.parent:
            self.parent.load()
            self.config = self.parent.config.get(self.name)
            # Initialize parent if necessary
            if self.config is None:
                self.parent.config[self.name] = {}
                self.config = {}

    def load(self):
        """Public load function

        Do not override"""
        self._load()

    def __getattr__(self, item):
        return self.config.get(item)

    def __getitem__(self, item):
        return self.config.get(item)

    def __setitem__(self, key, value):
        if self.parent:
            self.parent[self.name][key] = value
            self.config = self.parent[self.name]
        else:
            self.config[key] = value
        self.save()
