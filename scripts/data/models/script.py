from typing import Set
from typing import Union
from typing import Any
from typing import Iterator

import data.selection as queries

import data.models.base as util

class Script(util.ModelBase):
    _type = "script"
    _attributes = [
        "tags",
        "repr",
    ]

    def __init__(self, id: Any, tags: Set[str], repr: str=None) -> None:
        super(Script, self).__init__()
        self.id = bytearray(id).hex()
        self.tags = tags
        self.repr = repr

    def get_id(self):
        return self.id

    @classmethod
    def _sql(cls, cursor, meta, id=None) -> str:
        with_repr = meta.flags.get('with_repr', False)
        query_fn = queries.scripts_with_repr if with_repr else queries.scripts_without_repr
        return query_fn(cursor, **util.get_meta(meta), id=id)
