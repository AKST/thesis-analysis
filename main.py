import logging as l
import os.path as p

from os import listdir
from datetime import datetime, timedelta
from collections import namedtuple
from csv import DictReader as read_csv

from typing import IO
from typing import Dict
from typing import Union
from typing import Optional
from typing import Iterator
from typing import NamedTuple

class Analyzer:
    def __init__(self, meta_data: Dict[str, '_TaskMeta'], r_dir: str, w_dir: str, log: bool) -> None:
        self._meta_data = meta_data
        self._r_dir = r_dir
        self._w_dir = w_dir
        self._should_log = log

    def run(self) -> None:
        for package_info in _get_sub_dirs(self._r_dir):
            _log(self, 'info', "checking benchmarks for %s", package_info.name)
            for sub_dir in _get_sub_dirs(package_info.path):
                meta = self._meta_data[sub_dir.name]
                try:
                    task = TaskAnalyzer.create(meta, sub_dir.path, parent=self)
                    task.run()
                except InvalidTaskDir as e:
                    _log(self, 'warn', 'invalid task directory %s', e.task_dir)
                    continue

    @staticmethod
    def make_instance(r_dir: str, w_dir: str, log: bool = False) -> 'Analyzer':
        if not p.isdir(r_dir):
            raise ArgumentError("r_dir", "wasn't directory path")

        if not p.isdir(w_dir):
            raise ArgumentError("w_dir", "wasn't directory path")

        uuid_meta_filename = p.join(r_dir, "uuid-times.csv")
        if not p.isfile(uuid_meta_filename):
            raise ArgumentError("directory_name", "doesn't contain uuid times")

        # read the uuid meta file
        with open(uuid_meta_filename) as metafile:
            uuidmeta = { row['id']: _TaskMeta.create(**row) for row in read_csv(metafile) }

        return Analyzer(uuidmeta, r_dir, w_dir, log)

class TaskAnalyzer:
    def __init__(self, meta: '_TaskMeta',
                       task: Dict[str, '_TaskVersionMeta'],
                       path: str,
                       w_dir: str,
                       log: bool) -> None:
        self._meta = meta
        self._task = task
        self._path = path
        self._w_dir = w_dir
        self._should_log = log

    def run(self) -> None:
        for version, meta in self._task.items():
            _log(self, 'info', "%s has dir %s, ran for %ss", version, meta, meta.run_time)

    @staticmethod
    def create(meta: '_TaskMeta', path: str, parent: Analyzer) -> 'TaskAnalyzer':
        time_stamps_f = p.join(path, 'time_stamps.csv')
        if not p.isfile(time_stamps_f):
            raise InvalidTaskDir(path)

        with open(time_stamps_f, mode='r') as metafile:
            taskmeta = { row['version']: _TaskVersionMeta.create(**row) for row in read_csv(metafile) }

        return TaskAnalyzer(meta, taskmeta, path, parent._w_dir, parent._should_log)

# Util Classes

PackagePath = namedtuple("PackagePath", ['name', 'path'])

class _TaskMeta:
    """ representation of data in uuid-meta.csv"""
    def __init__(self, stime: datetime, id: str, package: str) -> None:
        self.package = package
        self.stime = stime
        self.id = id

    @staticmethod
    def create(stime: str, id: str, package: str) -> '_TaskMeta':
        try:
            as_int = int(stime)
            parsed = datetime.fromtimestamp(as_int)
            return _TaskMeta(parsed, id, package)
        except:
            raise CorruptDataError("stime is not a unix time stamp")

class _TaskVersionMeta:
    """ representation of data in uuid-meta.csv"""
    def __init__(self, version: str, stime: datetime, etime: datetime) -> None:
        self.version = version
        self.stime = stime
        self.etime = etime

    @property
    def run_time(self) -> float:
        return (self.etime - self.stime).total_seconds()

    def __str__(self) -> str:
        return "_TaskVersionMeta(%s, %s, %s)" % (self.version, self.stime, self.etime)

    @staticmethod
    def create(version: str, start: str, end: str) -> '_TaskVersionMeta':
        try:
            stime = _to_time(*map(int, start.split(':')))
            etime = _to_time(*map(int, end.split(':')))
            return _TaskVersionMeta(version, stime, etime)
        except:
            raise CorruptDataError("trouble parsing data")

# Util functions

def _get_sub_dirs(root: str) -> Iterator[PackagePath]:
    for name in listdir(root):
        full_path = p.join(root, name)
        if p.isdir(full_path):
            yield PackagePath(name, full_path)

def _log(loggable: Union[TaskAnalyzer, Analyzer], level: str, *args, **kwargs) -> None:
    if loggable._should_log:
        method = getattr(l, level)
        method(*args, **kwargs)

def _to_time(seconds: int, nano_seconds: int) -> datetime:
    time = datetime.fromtimestamp(seconds)
    return time.replace(microsecond=int(nano_seconds * 0.001))

def run_analysis(r_dir: str, w_dir: str, log=False):
    analysiser = Analyzer.make_instance(r_dir, w_dir, log)
    analysiser.run()

# Error Classes

class AnalysisError(Exception):
    pass

class CorruptDataError(AnalysisError):
    pass

class InvalidTaskDir(AnalysisError):
    def __init__(self, path, *args, **kwargs):
        message = "invalid task dir: '%s'" % path
        super(InvalidTaskDir, self).__init__(message, *args, **kwargs)
        self.task_dir = path

class ArgumentError(AnalysisError):
    def __init__(self, arg_name, *args, **kwargs):
        message = "'%s', %s" % (arg_name, problem)
        super(ArgumentError, self).__init__(message, *args, **kwargs)

class NotSpecifiedArg(ArgumentError):
    def __init__(self, arg_name, *args, **kwargs):
        super(NotSpecifiedArg, self).__init__(arg_name, "wasn't specfied", *args, **kwargs)

if __name__ == '__main__':
    from sys import argv, stdout

    l.basicConfig(level=1, format="[%(levelname)s %(asctime)s] :: %(message)s")

    if len(argv) < 3:
        l.error("Program requires 3 arguments")
        exit(1)
    else:
        data_folder = argv[1]
        dist_folder = argv[2]
        l.debug("reading data from %s", data_folder)
        l.debug("writing data to %s", dist_folder)
        try:
            run_analysis(r_dir=data_folder, w_dir=dist_folder, log=True)
        except AnalysisError as e:
            l.exception("%s", e)

