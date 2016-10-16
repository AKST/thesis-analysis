import logging as l
import os.path as p

from os import listdir
from collections import namedtuple
from csv import DictReader as read_csv

from typing import IO
from typing import Dict
from typing import NamedTuple

def run_analysis(r_dir, w_dir, log=False):
    analysiser = Analysiser.make_instance(r_dir, w_dir, log)
    analysiser.run()

TaskMeta = namedtuple("TaskMeta", ['stime', 'id', 'package'])
PackagePath = namedtuple("PackagePath", ['name', 'path'])

class Analysiser:
    def __init__(self, meta_data: Dict[str, TaskMeta], r_dir: str, w_dir: str, log: bool) -> None:
        self._meta_date = meta_data
        self._r_dir = r_dir
        self._w_dir = w_dir
        self._should_log = log

    def run(self):
        # directories with results of packages
        append_dir = lambda f: PackagePath(f, p.join(self._r_dir, f))
        check_dir  = lambda d: p.isdir(d.path)
        package_dirs = filter(check_dir, map(append_dir, listdir(self._r_dir)))

        for package_info in package_dirs:
            self._log('info', "checking benchmarks for %s", package_info.name)

    def _log(self, level, *args, **kwargs):
        if self._should_log:
            method = getattr(l, level)
            method(*args, **kwargs)

    @staticmethod
    def make_instance(r_dir: str, w_dir: str, log: bool = False):
        if not p.isdir(r_dir):
            raise ArgumentError("r_dir", "wasn't directory path")

        if not p.isdir(w_dir):
            raise ArgumentError("w_dir", "wasn't directory path")

        uuid_meta_filename = p.join(r_dir, "uuid-times.csv")
        if not p.isfile(uuid_meta_filename):
            raise ArgumentError("directory_name", "doesn't contain uuid times")

        # read the uuid meta file
        with open(uuid_meta_filename) as metafile:
            uuidmeta = { row['id']: TaskMeta(**row) for row in read_csv(metafile) }

        return Analysiser(uuidmeta, r_dir, w_dir, log)




class AnalysisError(Exception):
    pass

class ArgumentError(AnalysisError):
    def __init__(self, arg_name, problem, *args, **kwargs):
        message = "'%s', %s" % (arg_name, problem)
        super(ArgumentError, self).__init__(message, *args, **kwargs)

class NotSpecifiedArg(ArgumentError):
    def __init__(self, arg_name, *args, **kwargs):
        super(ArgumentError, self).__init__(arg_name, "wasn't specfied", *args, **kwargs)

if __name__ == '__main__':
    from sys import argv, stdout

    l.basicConfig(level="INFO", format="[%(levelname)s %(asctime)s] :: %(message)s")

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
            l.exception(e)

