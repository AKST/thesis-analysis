import logging as l
import os.path as p

from os       import listdir, stat as fs_stat, walk as fs_walk
from datetime import datetime, timedelta
from csv      import DictReader as read_csv

from typing import Any
from typing import Dict
from typing import Union
from typing import Tuple
from typing import Iterator

import common.util as util
import common.errors as errors
import data.inserts as queries


_NOT_SECRET_DIR = lambda name: not name.startswith('__')


class Analyzer:
    def __init__(self,
                 meta_data: Dict[str, util.TaskMeta],
                 r_dir: str,
                 package_meta: Dict[str, Any],
                 log: bool) -> None:
        """
        Consider using `make_instance' instead of the constructor directly
        """
        self._package_meta = package_meta
        self._meta_data = meta_data
        self._r_dir = r_dir
        self._should_log = log

    def insert_into(self, conn: Any) -> None:
        """
        Basically traverese over the directory and inserts all the junk into
        the database #YOLO #PleaseWriteMoreComprehensiveDocumentation #TODO
        """
        package_ids = {} # type Dict[str, int]
        with conn.cursor() as cursor:
            # create rows for each package, if not exist
            for package_info in util.get_sub_dirs(self._r_dir, _NOT_SECRET_DIR):
                package_meta = self._package_meta['target'][package_info.name]
                _id = queries.insert_package_get_id(cursor, package_info, package_meta)
                package_ids[package_info.name] = _id
                util.log(self, 'info', "inserting package for %s @ id %s", package_info.name, _id)

            for script in util.get_file_names(p.join(self._r_dir, '__checksums')):
                util.log(self, 'info', "inserting benchmark_script for %s", script.name)
                queries.insert_script(cursor, script)

            # create rows for each batch initiated, if not exist
            for key, meta in self._meta_data.items():
                queries.insert_batch(cursor, meta, package_ids)
                util.log(self, 'info', "inserting batch '%s' into db", key)

            for package_info in util.get_sub_dirs(self._r_dir, _NOT_SECRET_DIR):
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
                        util.log(self, 'info', "inserting result for '%s' of batch(id='%s')", result.version, meta.id)
                        queries.insert_result(cursor, result, meta)

    @staticmethod
    def make_instance(r_dir: str, meta: Dict[str, Any], log: bool = False) -> 'Analyzer':
        """
        Factory method of Analyzer which handles validation, using
        this is recommended over using the constructor directly unless
        validation on input has already been performed.
        """
        if not p.isdir(r_dir):
            raise errors.ArgumentError("r_dir", "wasn't directory path")

        uuid_meta_filename = p.join(r_dir, "uuid-times.csv")
        if not p.isfile(uuid_meta_filename):
            raise errors.ArgumentError("directory_name", "doesn't contain uuid times")

        # read the uuid meta file
        with open(uuid_meta_filename) as metafile:
            uuidmeta = { row['id']: util.TaskMeta.create(**row) for row in read_csv(metafile) }

        return Analyzer(uuidmeta, r_dir, meta, log)

class PackageResultAnalyzer:
    """This does anaylsis of a package included in a task"""
    def __init__(self, meta: util.TaskMeta,
                       task: Dict[str, util.PackageResultMeta],
                       path: str,
                       log: bool) -> None:
        self._meta = meta
        self._task = task
        self._path = path
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

        return PackageResultAnalyzer(meta, taskmeta, path, parent._should_log)

# entry point for analysis, which handles instances etc, etc, etc, etc....

def run_analysis(r_dir: str, meta: Dict[str, Any], log: bool = False, conn: Any = None) -> None:
    if conn is None:
        raise errors.MissingDBError()
    else:
        analysiser = Analyzer.make_instance(r_dir, meta, log)
        analysiser.insert_into(conn)

# Main function

if __name__ == '__main__':
    from psycopg2 import connect as db_connect

    from json import load as load_json_file
    from sys import stderr
    from os  import environ

    from data.connect import pg_connection
    from cli.config import setup_logging
    from cli.populate_args import parser as arg_parser

    args = arg_parser.parse_args()
    setup_logging(args)

    l.debug("reading data from %s", args.data_folder)

    try:
        with open(args.config_file, 'r') as f:
            config_meta = load_json_file(f)
        with pg_connection(args) as conn:
            run_analysis(r_dir=args.data_folder, meta=config_meta, log=True, conn=conn)
    except errors.PopulationError as e:
        l.exception("%s", e)

