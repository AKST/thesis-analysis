from typing import Set
from typing import Union
from typing import Any
from typing import Iterator
from decimal import Decimal
from datetime import datetime

import common.errors as errors
import data.selection as queries
import data.models.base as util

def format_version(version: str) -> str:
    return version.replace(",", ".")[1:-1]

class ResultsReadable(util.ModelBase):
    _type = "result_readable"
    _attributes = [
        "package_name",
        "ghc_version",
        "file_extension",
        "average_time",
        "file_size",
        "script_tags",
    ]
    _relations = {
        "script_hash": "script",
    }

    def __init__(self,
            package_name: str,
            ghc_version: str,
            file_extension: str,
            average_time: Decimal,
            file_size: Decimal,
            script_hash: Any,
            script_tags: Set[str],
            script_age: datetime) -> None:
        super(ResultsReadable, self).__init__()
        self.package_name = package_name
        self.ghc_version = format_version(ghc_version)
        self.file_extension = file_extension
        self.average_time = average_time
        self.file_size = file_size
        self.script_hash = bytearray(script_hash).hex()
        self.script_tags = script_tags
        self.script_age = script_age

    def get_id(self):
        return "%s:%s:%s" % (self.package_name, self.ghc_version, self.script_hash)

    @classmethod
    def _sql(cls, cursor, meta, id=None) -> str:
        if id != None:
            raise errors.IllegalOperation()
        return queries.get_results(meta.flags, api=False)(cursor, **util.get_meta(meta))

class ResultsAPI(util.ModelBase):
    _type = "result"
    _attributes = [
        "ghc_version",
        "file_extension",
        "average_time",
        "file_size",
    ]
    _relations = {
        "script_hash": { "type": "script", "name": "script" },
        "package_id": { "type": "package", "name": "package" },
    }

    def __init__(self,
            package_id: str,
            ghc_version: str,
            file_extension: str,
            average_time: Decimal,
            file_size: Decimal,
            script_hash: Any) -> None:
        super(ResultsAPI, self).__init__()
        self.package_id = package_id
        self.ghc_version = format_version(ghc_version)
        self.file_extension = file_extension
        self.average_time = average_time
        self.file_size = file_size
        self.script_hash = bytearray(script_hash).hex()

    def get_id(self):
        return "%s:%s:%s:%s" % (self.package_id, self.ghc_version, self.file_extension, self.script_hash)

    @classmethod
    def _sql(cls, cursor, meta, id=None) -> str:
        if id != None:
            raise errors.IllegalOperation()
        query = queries.get_results(meta.flags, api=True)
        return query(cursor, **util.get_meta(meta))
