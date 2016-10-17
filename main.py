import logging as l
import os.path as p

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

import util
import errors
import queries


class Analyzer:
    def __init__(self,
                 meta_data: Dict[str, util.TaskMeta],
                 r_dir: str,
                 log: bool,
                 conn: Any) -> None:
        self._conn = conn
        self._meta_data = meta_data
        self._r_dir = r_dir
        self._should_log = log

    def analysis(self) -> None:
        package_ids = {} # type Dict[str, int]
        with self._conn.cursor() as cursor:
            # create rows for each package, if not exist
            for package_info in util.get_sub_dirs(self._r_dir):
                _id = queries.insert_package_get_id(cursor, package_info)
                package_ids[package_info.name] = _id
                util.log(self, 'info', "inserting package for %s @ id %s", package_info.name, _id)

            # create rows for each batch initiated, if not exist
            for key, meta in self._meta_data.items():
                queries.insert_batch(cursor, meta, package_ids)

        for package_info in util.get_sub_dirs(self._r_dir):
            util.log(self, 'info', "checking benchmarks for %s", package_info.name)
            for sub_dir in util.get_sub_dirs(package_info.path):
                meta = self._meta_data[sub_dir.name]

                try:
                    task = PackageResultAnalyzer.create(meta, sub_dir.path, parent=self)
                except errors.InvalidTaskDir as e:
                    util.log(self, 'warn', 'invalid task directory %s', e.task_dir)
                    continue

                for result in task.results():
                    util.log(self, 'debug', "%s", result)

    @staticmethod
    def make_instance(r_dir: str, log: bool = False, conn: Any = None) -> 'Analyzer':
        if conn is None:
            raise errors.MissingDBError()

        if not p.isdir(r_dir):
            raise errors.ArgumentError("r_dir", "wasn't directory path")

        uuid_meta_filename = p.join(r_dir, "uuid-times.csv")
        if not p.isfile(uuid_meta_filename):
            raise errors.ArgumentError("directory_name", "doesn't contain uuid times")

        # read the uuid meta file
        with open(uuid_meta_filename) as metafile:
            uuidmeta = { row['id']: util.TaskMeta.create(**row) for row in read_csv(metafile) }

        return Analyzer(uuidmeta, r_dir, log, conn)

class PackageResultAnalyzer:
    """This does anaylsis of a package included in a task"""
    def __init__(self, meta: util.TaskMeta,
                       task: Dict[str, util.PackageResultMeta],
                       path: str,
                       log: bool,
                       conn: Any) -> None:
        self._meta = meta
        self._task = task
        self._path = path
        self._conn = conn
        self._should_log = log

    def _calc_build_size(self, version: str) -> Iterator[util.FSize]:
        build_path = p.join(self._path, '%s-build' % version)
        for root, dirs, files in fs_walk(build_path):
            for f in files:
                try:
                    path = p.join(root, f)
                    yield util.FSize.create(version, path, fs_stat(path).st_size)
                except:
                    util.log(self, 'warn', "couldn't read file %s", path)

    def results(self) -> Iterator[util.PackageVersionResult]:
        for version, meta in self._task.items():
            yield util.PackageVersionResult(version, meta.run_time, [*self._calc_build_size(version)])

    @staticmethod
    def create(meta: util.TaskMeta, path: str, parent: Analyzer) -> 'PackageResultAnalyzer':
        time_stamps_f = p.join(path, 'time_stamps.csv')
        if not p.isfile(time_stamps_f):
            raise errors.InvalidTaskDir(path)

        with open(time_stamps_f, mode='r') as metafile:
            taskmeta = { row['version']: util.PackageResultMeta.create(**row) for row in read_csv(metafile) }

        return PackageResultAnalyzer(meta, taskmeta, path, parent._should_log, parent._conn)


def run_analysis(r_dir: str, log: bool = False, conn: Any = None) -> None:
    analysiser = Analyzer.make_instance(r_dir, log, conn)
    analysiser.analysis()

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
        except errors.AnalysisError as e:
            l.exception("%s", e)

