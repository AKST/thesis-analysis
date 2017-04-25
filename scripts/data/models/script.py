from typing import Set
from typing import Union
from typing import Any
from typing import Iterator
from datetime import datetime

import data.selection as queries

import data.models.base as util

class Script(util.ModelBase):
    _type = "script"
    _attributes = [
        "tags",
        "repr",
        "last_modified",
    ]

    def __init__(self, id: Any, tags: Set[str], last_modified: datetime, repr: str=None) -> None:
        super(Script, self).__init__()
        self.id = bytearray(id).hex()
        self.tags = tags
        self.repr = repr
        self.last_modified = last_modified

    def get_id(self):
        return self.id

    @classmethod
    def _sql(cls, cursor, meta, id=None) -> str:
        with_repr = meta.flags.get('with_repr', False)
        query_fn = queries.get_scripts(meta.flags, id=id)
        return query_fn(cursor, **util.get_meta(meta))
