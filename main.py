
import logging as l
import os.path as p
import semver

from os import listdir, stat as fs_stat, walk as fs_walk
from datetime import datetime, timedelta
from csv import DictReader as read_csv

from typing import IO
from typing import Any
from typing import Dict
from typing import List
from typing import Union
from typing import Tuple
from typing import Optional
from typing import Iterator
from typing import NamedTuple


class Analyzer:
    def __init__(self,
                 meta_data: Dict[str, '_TaskMeta'],
                 r_dir: str,
                 log: bool,
                 conn: Any) -> None:
        self._conn = conn
        self._meta_data = meta_data
        self._r_dir = r_dir
        self._should_log = log

    def analysis(self) -> None:
        for package_info in _get_sub_dirs(self._r_dir):
            _log(self, 'info', "checking benchmarks for %s", package_info.name)
            for sub_dir in _get_sub_dirs(package_info.path):
                meta = self._meta_data[sub_dir.name]

                try:
                    task = PackageResultAnalyzer.create(meta, sub_dir.path, parent=self)
                except InvalidTaskDir as e:
                    _log(self, 'warn', 'invalid task directory %s', e.task_dir)
                    continue

                for result in task.results():
                    _log(self, 'debug', "%s", result)

    @staticmethod
    def make_instance(r_dir: str, log: bool = False, conn: Any = None) -> 'Analyzer':
        if conn is None:
            raise MissingDBError()

        if not p.isdir(r_dir):
            raise ArgumentError("r_dir", "wasn't directory path")

        uuid_meta_filename = p.join(r_dir, "uuid-times.csv")
        if not p.isfile(uuid_meta_filename):
            raise ArgumentError("directory_name", "doesn't contain uuid times")

        # read the uuid meta file
        with open(uuid_meta_filename) as metafile:
            uuidmeta = { row['id']: _TaskMeta.create(**row) for row in read_csv(metafile) }

        return Analyzer(uuidmeta, r_dir, log, conn)

class PackageResultAnalyzer:
    """This does anaylsis of a package included in a task"""
    def __init__(self, meta: '_TaskMeta',
                       task: Dict[str, '_PackageResultMeta'],
                       path: str,
                       log: bool,
                       conn: Any) -> None:
        self._meta = meta
        self._task = task
        self._path = path
        self._conn = conn
        self._should_log = log

    def _calc_build_size(self, version: str) -> Iterator['_FSize']:
        build_path = p.join(self._path, '%s-build' % version)
        for root, dirs, files in fs_walk(build_path):
            for f in files:
                try:
                    path = p.join(root, f)
                    yield _FSize.create(version, path, fs_stat(path).st_size)
                except:
                    _log(self, 'warn', "couldn't read file %s", path)

    def results(self) -> Iterator['_PackageVersionResult']:
        for version, meta in self._task.items():
            yield _PackageVersionResult(version, meta.run_time, [*self._calc_build_size(version)])

    @staticmethod
    def create(meta: '_TaskMeta', path: str, parent: Analyzer) -> 'PackageResultAnalyzer':
        time_stamps_f = p.join(path, 'time_stamps.csv')
        if not p.isfile(time_stamps_f):
            raise InvalidTaskDir(path)

        with open(time_stamps_f, mode='r') as metafile:
            taskmeta = { row['version']: _PackageResultMeta.create(**row) for row in read_csv(metafile) }

        return PackageResultAnalyzer(meta, taskmeta, path, parent._should_log, parent._conn)

# Util Classes

class PackagePath:
    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.path = path

    def __str__(self) -> str:
        return "PackagePath('%s', '%s')" % (self.name, self.path)

class _PackageVersionResult:
    def __init__(self, version: str, compile_time: float, file_sizes: List['_FSize']) -> None:
        self.version = version
        self.compile_time = compile_time
        self.file_sizes = file_sizes

    def __str__(self) -> str:
        return "_PackageVersionResult(version='%s', compile_time=%s, file_sizes=[%s])" % \
                (self.version, self.compile_time, ', '.join(map(str, self.file_sizes)))

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

class _PackageResultMeta:
    """ representation of data in uuid-meta.csv"""
    def __init__(self, version: str, stime: datetime, etime: datetime) -> None:
        self.version = version
        self.stime = stime
        self.etime = etime

    @property
    def run_time(self) -> float:
        return (self.etime - self.stime).total_seconds()

    def __str__(self) -> str:
        return "_PackageResultMeta(version='%s', stime='%s', etime='%s')" % (self.version, self.stime, self.etime)

    @staticmethod
    def create(version: str, start: str, end: str) -> '_PackageResultMeta':
        try:
            stime = _to_time(*map(int, start.split(':')))
            etime = _to_time(*map(int, end.split(':')))
            return _PackageResultMeta(version, stime, etime)
        except:
            raise CorruptDataError("trouble parsing data")

class _FSize:
    def __init__(self, path: str, extension: str, size: int) -> None:
        self.path      = path
        self.extension = extension
        self.size      = size

    @staticmethod
    def create(version: str, path: str, size: int) -> '_FSize':
        rel_path = path.split("%s-build" % version)[1]
        f_ext = rel_path.split('.')[-1]
        return _FSize(rel_path, f_ext, size)

    def __str__(self):
        return "_FSize(path='%s', extension='%s', size='%s')" % (self.path, self.extension, self.size)

# Util functions

def _get_sub_dirs(root: str) -> Iterator[PackagePath]:
    for name in listdir(root):
        full_path = p.join(root, name)
        if p.isdir(full_path):
            yield PackagePath(name, full_path)

def _log(loggable: Union[PackageResultAnalyzer, Analyzer], level: str, *args, **kwargs) -> None:
    if loggable._should_log:
        method = getattr(l, level)
        method(*args, **kwargs)

def _to_time(seconds: int, nano_seconds: int) -> datetime:
    time = datetime.fromtimestamp(seconds)
    return time.replace(microsecond=int(nano_seconds * 0.001))

def run_analysis(r_dir: str, log: bool = False, conn: Any = None) -> None:
    analysiser = Analyzer.make_instance(r_dir, log, conn)
    analysiser.analysis()

# Error Classes

class AnalysisError(Exception):
    pass

class MissingDBError(AnalysisError):
    def __init__(self, *args, **kwargs):
        message = "expected db connection"
        super(MissingDBError, self).__init__(message, *args, **kwargs)

class CorruptDataError(AnalysisError):
    def __init__(self, *args, **kwargs):
        message = "data corruption"
        super(CorruptDataError, self).__init__(message, *args, **kwargs)

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

# Main function

if __name__ == '__main__':
    from psycopg2 import connect as db_connect
    from sys import argv, stderr
    from os  import environ


    THESIS_L_FMT_DEFAULT = "[%(levelname)s %(asctime)s] :: %(message)s"
    THESIS_L_LEVEL_FLAG  = 'THESIS_L_LEVEL'
    THESIS_L_FMT_FLAG    = 'THESIS_L_FORMAT'
    THESIS_PG_DB_FLAG    = 'THESIS_PG_DB'
    THESIS_PG_HOST_FLAG  = 'THESIS_PG_HOST'
    THESIS_PG_USER_FLAG  = 'THESIS_PG_USER'
    THESIS_PG_PSWD_FLAG  = 'THESIS_PG_PSWD'

    def get_logging_level() -> Tuple[int, Union[None, str]]:
        l_level = environ.get(THESIS_L_LEVEL_FLAG, 'ERROR')
        if hasattr(l, l_level):
            return getattr(l, l_level), None
        else:
            return l.ERROR, ("'%s' is not a valid logging level" % l_level)

    def pg_connection() -> Any:
        dbname = environ.get(THESIS_PG_DB_FLAG, 'thesis-data')
        host = environ.get(THESIS_PG_HOST_FLAG, 'localhost')
        user = environ.get(THESIS_PG_USER_FLAG, 'postgres')
        pswd = environ.get(THESIS_PG_PSWD_FLAG, '')
        return db_connect(host=host, dbname=dbname, user=user, password=pswd)

    log_fmt = environ.get(THESIS_L_FMT_FLAG, THESIS_L_FMT_DEFAULT)
    log_lvl, err_msg = get_logging_level()
    l.basicConfig(level=log_lvl, format=log_fmt)

    if isinstance(err_msg, str):
        l.error("Non fatal error, but FYI; %s...", err_msg)

    if len(argv) < 2:
        l.error("Program requires 2 arguments")
        exit(1)
    else:
        data_folder = argv[1]
        l.debug("reading data from %s", data_folder)
        try:
            with pg_connection() as conn:
                run_analysis(r_dir=data_folder, log=True, conn=conn)
        except AnalysisError as e:
            l.exception("%s", e)

