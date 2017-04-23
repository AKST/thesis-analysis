from abc import ABCMeta, abstractmethod
from typing import Any
from decimal import Decimal
import json

class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ModelBase):
            return {
                "id": obj.get_id(),
                "type": obj.get_type(),
                "data": {
                    "attributes": obj.get_attributes(),
                    "relations": obj.get_relations()
                }
            }
        else:
            return json.JSONEncoder.default(self, obj)

class ModelBase(metaclass=ABCMeta):
    _type = None
    _attributes = None
    _relations = None
    def __init__(self):
        pass

    def get_type(self):
        return self._type

    @abstractmethod
    def get_id(self):
        raise NotImplemented()

    def get_attributes(self):
        attrs = {}
        if not self._attributes:
            return None
        for key in self._attributes:
            value = getattr(self, key)
            if isinstance(value, Decimal):
                attrs[key] = float(value)
            else:
                attrs[key] = value
        return attrs

    def get_relations(self):
        rels = {}
        if not self._relations:
            return None

        def get_label(name, ty):
            return ty['name'] if isinstance(ty, dict) else name

        def get_type(ty):
            return ty['type'] if isinstance(ty, dict) else ty

        for name, ty in self._relations.items():
            value = getattr(self, name)
            label = get_label(name, ty)
            _type = get_type(ty)
            if isinstance(value, list):
                rels[label] = []
                for entry in value:
                    rels[label].append({
                        "type": _type,
                        "id": entry,
                    })
            else:
                rels[label] = {
                    "type": _type,
                    "id": value,
                }
        return rels

    @classmethod
    def _sql(cls, cursor, meta, id=None):
        raise NotImplemented()

    @classmethod
    def find(cls, conn, meta=None):
        cursor = conn.cursor()
        cursor.execute(cls._sql(cursor, meta, id=meta.query_id))
        return apply_to_constructor(cls, cursor, label=cls._type)

    @classmethod
    def all(cls, conn, meta=None):
        cursor = conn.cursor()
        cursor.execute(cls._sql(cursor, meta))
        return apply_to_constructor(cls, cursor, label=cls._type)

class ModelCursor:
    def __init__(self, items, names, cursor, label=None):
        self.label = label
        self._names = names
        self._items = items
        self._cursor = cursor

    def names(self):
        return self._names

    def as_tuple(self, entry):
        return [getattr(entry, colname) for colname in self.names()]

    def __iter__(self):
        return self._items

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self._cursor.close()

def apply_to_constructor(fn, cursor, label=None):
    names = [desc.name for desc in cursor.description]
    items = (fn(**({ k: v for (k, v) in zip(names, row) })) for row in cursor)
    return ModelCursor(items, names, cursor, label=label)

def get_meta(config: Any):
    if config != None:
        return { 'count': config.query_count, 'offset': config.query_offset }
    else:
        return {}
