from collections.abc import MutableSet
from collections import OrderedDict


class OrderedSet(MutableSet):
    """ A set collection that remembers the elements first insertion order. """

    __slots__ = ["_map"]

    def __init__(self, elems=()):
        self._map = OrderedDict((elem, None) for elem in elems)

    def __contains__(self, elem):
        return elem in self._map

    def __iter__(self):
        return iter(self._map)

    def __len__(self):
        return len(self._map)

    def add(self, elem):
        self._map[elem] = None

    def discard(self, elem):
        self._map.pop(elem, None)
