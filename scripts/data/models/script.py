from typing import Set
from typing import Union
from typing import Any
from typing import Iterator

import data.selection as queries

import data.models.base as util

class Script(util.ModelBase):
    def __init__(self, id: Any, tags: Set[str], repr: str=None) -> None:
        super(Script, self).__init__("script", [
            "tags",
            "repr",
        ])
        self.id = bytearray(id).hex()
        self.tags = tags
        self.repr = repr

    def get_id(self):
        return self.id

    def __repr__(self):
        return 'Script(id=%s, tags=%s, repr=%s)' \
            % (self.id, self.tags, self.repr)

    @classmethod
    def all(cls, conn, meta=None, **kwargs) -> Iterator['Script']:
        with_repr = kwargs.get('with_repr', False)
        cursor = conn.cursor()
        query_fn = queries.scripts_with_repr if with_repr else queries.scripts_without_repr
        cursor.execute(query_fn(cursor, **util.get_meta(meta)))
        return util.apply_to_constructor(Script, cursor, label='script')
