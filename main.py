import logging as l
import os.path as p
from os import listdir
from collections import namedtuple
from csv import DictReader as read_csv


def run_analysis(directory_name, writeTo=None, log=False):
    if writeTo is None:
        raise NotSpecifiedArg("writeTo")

    if not p.isdir(directory_name):
        raise ArgumentError("directory_name", "wasn't directory path")

    uuid_meta_filename = p.join(directory_name, "uuid-times.csv")
    if not p.isfile(uuid_meta_filename):
        raise ArgumentError("directory_name", "doesn't contain uuid times")

    # directories with results of packages
    append_dir = lambda f: PackagePath(f, "%s%s" % (directory_name, f))
    check_dir  = lambda d: p.isdir(d.path)
    package_dirs = filter(check_dir, map(append_dir, listdir(directory_name)))

    # read the uuid meta file
    with open(uuid_meta_filename) as metafile:
        uuidmeta = { row['id']: TaskMeta(**row) for row in read_csv(metafile) }

    for package_path in package_dirs:
        l.info(str(package_path))


TaskMeta = namedtuple("TaskMeta", ('stime', 'id', 'package'))
PackagePath = namedtuple("PackagePath", ('name', 'path'))


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

    if len(argv) < 2:
        l.error("Program requires 2 arguments")
        exit(1)
    else:
        data_folder = argv[1]
        l.info("Starting default mode, checking %s for data", data_folder)
        try:
            run_analysis(data_folder, writeTo=stdout, log=True)
        except AnalysisError as e:
            l.exception(e)

