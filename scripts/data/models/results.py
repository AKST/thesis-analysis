from typing import Set
from typing import Union
from typing import Any
from typing import Iterator
from decimal import Decimal
from datetime import datetime

import data.selection as queries
import data.models.base as util

def format_version(version: str) -> str:
    return version.replace(",", ".")

class ResultsReadable(util.ModelBase):
    def __init__(self,
            package_name: str,
            ghc_version: str,
            file_extension: str,
            average_time: Decimal,
            file_size: Decimal,
            script_hash: Any,
            script_tags: Set[str],
            script_age: datetime) -> None:
        super(ResultsAPI, self).__init__("result_readable", [
            "package_name",
            "ghc_version",
            "file_extension",
            "average_time",
            "file_size",
            "script_tags",
            "script_age",
        ], {
            "script_hash": "script",
        })
        super(ResultsReadable, self).__init__()
        self.package_name = package_name
        self.ghc_version = format_version(ghc_version)
        self.file_extension = file_extension
        self.average_time = average_time
        self.file_size = file_size
        self.script_hash = bytearray(script_hash).hex()
        self.script_tags = script_tags
        self.script_age = script_age

    @classmethod
    def all(cls, conn, meta=None, **kwargs) -> Iterator['ResultsReadable']:
        query = queries.get_results(meta.flags, api=False)
        cursor = conn.cursor()
        cursor.execute(query(cursor, **util.get_meta(meta)))
        return util.apply_to_constructor(ResultsReadable, cursor, label='results')

class ResultsAPI(util.ModelBase):
    def __init__(self,
            package_id: str,
            ghc_version: str,
            file_extension: str,
            average_time: Decimal,
            file_size: Decimal,
            script_hash: Any) -> None:
        super(ResultsAPI, self).__init__("result", [
            "ghc_version",
            "file_extension",
            "average_time",
            "file_size",
        ], {
            "package_id": "package",
            "script_hash": "script",
        })
        self.package_id = package_id
        self.ghc_version = format_version(ghc_version)[1:-1]
        self.file_extension = file_extension
        self.average_time = average_time
        self.file_size = file_size
        self.script_hash = bytearray(script_hash).hex()

    def get_id(self):
        return "%s:%s:%s" % (self.package_id, self.ghc_version, self.script_hash)

    @classmethod
    def all(cls, conn, meta=None, **kwargs) -> Iterator['ResultsAPI']:
        query = queries.get_results(meta.flags, api=True)
        cursor = conn.cursor()
        cursor.execute(query(cursor, **util.get_meta(meta)))
        return util.apply_to_constructor(ResultsAPI, cursor, label='results')
