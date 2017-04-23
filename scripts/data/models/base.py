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
    def __init__(self, type, attributes=None, relations=None):
        self._type = type
        self._attrs = attributes or []
        self._rels = relations or {}

    def get_type(self):
        return self._type

    @abstractmethod
    def get_id(self):
        raise NotImplemented()

    def get_attributes(self):
        attrs = {}
        for key in self._attrs:
            value = getattr(self, key)
            if isinstance(value, Decimal):
                attrs[key] = float(value)
            else:
                attrs[key] = value
        return attrs

    def get_relations(self):
        rels = {}
        for name, ty in self._rels.items():
            value = getattr(self, name)
            if isinstance(value, list):
                rels[name] = []
                for entry in value:
                    rels[name].append({
                        "type": ty,
                        "id": entry,
                    })
            else:
                rels[name] = {
                    "type": ty,
                    "id": value,
                }
        return rels

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
