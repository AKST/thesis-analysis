import logging
from json import dump as dump_json
from decimal import Decimal
from functools import reduce

import common.errors as errors
from data.models.base import ModelEncoder


def format_csv(w_file, cursor, **kwargs):
    def _fmt_col(item):
        if isinstance(item, str):
            return item
        elif isinstance(item, list):
            head = item[0]
            tail = item[1:]
            func = lambda a, b: '%s|%s' % (a, b)
            return '[%s]' % reduce(func, map(_fmt_col, tail), _fmt_col(head))
        else:
            return str(item)

    print(','.join(cursor.names()), file=w_file)
    for row in cursor:
        row_tuple = map(_fmt_col, cursor.as_tuple(row))
        print(','.join(row_tuple), file=w_file)

def format_json(w_file, cursor, single=False, **kwargs):
    entries = []
    resource = {
        "meta": {},
        "data": entries,
        "jsonapi": { "version": "1.0" },
    }
    if cursor.label:
        resource['meta']['type'] = cursor.label

    for row in cursor:
        entries.append(row)

    if single and len(entries) < 1:
        raise errors.UnknownResource()
    elif single and len(entries) > 0:
        resource['data'] = entries[0]
    dump_json(resource, w_file, cls=ModelEncoder)

def format_into(w_file, fmt, cursor, **kwargs):
    if fmt == 'csv':
        format_csv(w_file, cursor, **kwargs)
    elif fmt == 'json':
        format_json(w_file, cursor, **kwargs)

def from_db(Model, conn, output, args):
    if args.query_id:
        with Model.find(conn, args) as items:
            format_into(output, fmt=args.format, cursor=items, single=True)
    else:
        with Model.all(conn, args) as items:
            format_into(output, fmt=args.format, cursor=items)


if __name__ == '__main__':
    from sys import stdout, exit


    from data.models.script import Script
    from data.models.package import Package
    from data.models.results import ResultsReadable, ResultsAPI
    from data.models.filetype import FileType
    from data.connect import pg_connection
    from cli.config import setup_logging
    from cli.format_args import parser as arg_parser

    model_lookup = {
        'thesis.benchmark_script': Script,
        'thesis.results_readable': ResultsReadable,
        'thesis.results_api': ResultsAPI,
        'thesis.package': Package,
        'thesis.filetype': FileType,
    }

    args = arg_parser.parse_args()
    view = args.db_view
    setup_logging(args)
    logging.debug("args: %s", args)

    Model = model_lookup.get(view, None)
    if not Model:
        logging.error("%(view)s is not a db view" % locals())
        exit(1)

    try:
        with pg_connection(args) as conn:
            from_db(Model, conn, stdout, args)
    except errors.ThesisError as e:
        logging.error("an error occured '%s'" % e)
        logging.error(str(e))
