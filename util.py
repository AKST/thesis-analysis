import logging as l
import os.path as p

from os import listdir
from datetime import datetime, timedelta

from typing import Any
from typing import Iterator
from typing import Union
from typing import List


import errors

class PackagePath:
    def __init__(self, name: str, path: str, id: Union[None, int] = None) -> None:
        self.name = name
        self.path = path
        self.id = id

    def __str__(self) -> str:
        return "PackagePath('%s', '%s')" % (self.name, self.path)

class PackageVersionResult:
    def __init__(self, version: str, compile_time: float, file_sizes: List['FSize']) -> None:
        self.version = version
        self.compile_time = compile_time
        self.file_sizes = file_sizes

    def __str__(self) -> str:
        return "_PackageVersionResult(version='%s', compile_time=%s, file_sizes=[%s])" % \
                (self.version, self.compile_time, ', '.join(map(str, self.file_sizes)))

class TaskMeta:
    """ representation of data in uuid-meta.csv"""
    def __init__(self, stime: datetime, id: str, package: str) -> None:
        self.package = package
        self.stime = stime
        self.id = id

    @staticmethod
    def create(stime: str, id: str, package: str) -> 'TaskMeta':
        try:
            as_int = int(stime)
            parsed = datetime.fromtimestamp(as_int)
            return TaskMeta(parsed, id, package)
        except:
            raise errors.CorruptDataError("stime is not a unix time stamp")

class PackageResultMeta:
    """ representation of data in uuid-meta.csv"""
    def __init__(self, version: str, stime: datetime, etime: datetime) -> None:
        self.version = version
        self.stime = stime
        self.etime = etime

    @property
    def run_time(self) -> float:
        return (self.etime - self.stime).total_seconds()

    def __str__(self) -> str:
        return "PackageResultMeta(version='%s', stime='%s', etime='%s')" % (self.version, self.stime, self.etime)

    @staticmethod
    def create(version: str, start: str, end: str) -> 'PackageResultMeta':
        try:
            stime = to_time(*map(int, start.split(':')))
            etime = to_time(*map(int, end.split(':')))
            return PackageResultMeta(version, stime, etime)
        except:
            raise errors.CorruptDataError("trouble parsing data")

class FSize:
    def __init__(self, path: str, extension: str, size: int) -> None:
        self.path      = path
        self.extension = extension
        self.size      = size

    @staticmethod
    def create(version: str, path: str, size: int) -> 'FSize':
        rel_path = path.split("%s-build" % version)[1]
        f_ext = rel_path.split('.')[-1]
        return FSize(rel_path, f_ext, size)

    def __str__(self):
        return "FSize(path='%s', extension='%s', size='%s')" % (self.path, self.extension, self.size)


def get_sub_dirs(root: str) -> Iterator[PackagePath]:
    for name in listdir(root):
        full_path = p.join(root, name)
        if p.isdir(full_path):
            yield PackagePath(name, full_path)

def log(loggable: Any, level: str, *args, **kwargs) -> None:
    if loggable._should_log:
        method = getattr(l, level)
        method(*args, **kwargs)

def to_time(seconds: int, nano_seconds: int) -> datetime:
    time = datetime.fromtimestamp(seconds)
    return time.replace(microsecond=int(nano_seconds * 0.001))


