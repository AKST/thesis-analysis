from typing import Set
from typing import Union
from typing import Any
from typing import Iterator

import common.errors as errors
import data.selection as queries
import data.models.base as util


class Version(util.ModelBase):
    _type = "ghc_versions"
    _attributes = [
        "rank",
        "version",
    ]
    def __init__(self, version, rank: str) -> None:
        super(Version, self).__init__()
        self.version = version
        self.file_type = file_type

    def get_id(self):
        return self.version

    @classmethod
    def _sql(cls, cursor, meta, id=None) -> str:
        if id != None:
            raise errors.IllegalOperation()
        return queries.get_filetypes(cursor, **util.get_meta(meta))
