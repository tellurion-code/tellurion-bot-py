"""Zobrist Hashing, with decorators"""

import random

def _get_hash_from_table(table, key):
    if key not in table: table[key] = random.getrandbits(64)
    return table[key]


def _process_flag(name: str, flag: str):
    flag_set = False
    if flag in name:
        name = name.replace(flag, '')
        flag_set = True

    return name, flag_set


def _get_zobrist_hash(self):
    fields: tuple[str] = self.zobrist_fields
    if fields == '__all__': fields = self.__dict__.keys()
    _hash = 0

    for name in fields:
        name, no_key = _process_flag(name, "__no_key")   # Even if it's a dict, list, or tuple, we don't care about the order

        if name not in self._zobrist_hash: self._zobrist_hash[name] = {}
        zobrist_table = self._zobrist_hash[name]
        value = getattr(self, name) if name != "self" else self

        _hash ^= _hash_value(zobrist_table, value, no_key)
    
    return _hash

def _hash_value(zobrist_table, value, no_key):
    # Don't hash methods or classes
    if callable(value): return 0

    vtype = type(value)

    # Simple types
    if value is None or vtype in (int, float, complex, bool, str, bytes, bytearray):
        return _get_hash_from_table(zobrist_table, value)

    # Unordered collections
    if vtype in (frozenset, set) or no_key:
        _hash = 0
        for element in value:
            _hash ^= _hash_value(zobrist_table, element, False)
        
        return _hash

    # Ordered collections
    if vtype in (list, tuple, dict):
        _hash = 0
        if vtype == dict:
            items = value.items() 
        else:
            items = enumerate(value)

        for k, element in items:
            _hash ^= _get_hash_from_table(zobrist_table, (k, element))
        
        return _hash
    
    # User defined zobrist hashable types
    if hasattr(vtype, "_zobrist_hash"):
        return hash(value)

    # User-defined normally hashable types
    if hasattr(vtype, "__hash__") and hasattr(vtype, "__eq__"):
        return _get_hash_from_table(zobrist_table, value)
    
    return 0


def _process_class(cls, fields):
    cls._zobrist_hash = {}
    cls.zobrist_fields = fields or '__all__'

    cls.__hash__ = _get_zobrist_hash

    return cls


def zobrist_hash(cls=None, /, *, fields=None):
    """
    Implements Zobrish hashing into the class as its hash.

    Uses the fields named in fields to do the hashing. If it's not specified, will use all of the instance's fields.
    Only hashable assets (or ones specified below) will be used for the hashing, including Zobrist-hashable classes.

    For simple types like int or bool, the hashing is a random 64-bit number for each value that has been recorded.
    For collections, the hashing is done on each individual value.
    For ordered collections, the hashing takes into account the order/key of the values.
    """
    def wrap(cls):
        return _process_class(cls, fields)

    if cls is None:
        return wrap

    return wrap(cls)
