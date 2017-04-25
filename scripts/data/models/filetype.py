from typing import Set
from typing import Union
from typing import Any
from typing import Iterator

import common.errors as errors
import data.selection as queries
import data.models.base as util


class FileType(util.ModelBase):
    _type = "filetype"
    _attributes = [
        "file_type",
    ]
    def __init__(self, file_type: str) -> None:
        super(FileType, self).__init__()
        self.file_type = file_type

    def get_id(self):
        return self.file_type

    @classmethod
    def _sql(cls, cursor, meta, id=None) -> str:
        if id != None:
            raise errors.IllegalOperation()
        return queries.get_filetypes(cursor, **util.get_meta(meta))
