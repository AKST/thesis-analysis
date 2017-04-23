from typing import Set
from typing import Union
from typing import Any
from typing import Iterator

import data.selection as queries
import data.models.base as util

def format_version(version: str) -> str:
    return version.replace(",", ".")[1:-1]

class Package(util.ModelBase):
    _type = "package"
    _attributes = [
        "name",
        "commit_hash",
        "repo_url",
        "min_ghc",
        "max_ghc",
    ]
    def __init__(self,
            id: str,
            name: str,
            commit_hash: str,
            repo_url: str,
            min_ghc: str,
            max_ghc: str,
            activity_timestamp) -> None:
        super(Package, self).__init__()
        self.id = id
        self.name = name
        self.commit_hash =commit_hash
        self.repo_url = repo_url
        self.min_ghc = format_version(min_ghc)
        self.max_ghc = format_version(max_ghc)
        self.activity_timestamp = activity_timestamp

    def get_id(self):
        return self.id

    @classmethod
    def _sql(cls, cursor, meta, id=None) -> str:
        return queries.get_package(cursor, id=id, **util.get_meta(meta))

