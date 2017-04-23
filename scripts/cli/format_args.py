import argparse
import cli.common_args as common

_description = 'Formats results from the data base'
_name_of_view = 'name of the view which requires are produced on'
_id_lookup_help = 'if you want to look up a specific id then specify it with this flag'
_file_format = 'the output format of the command'
_offset_help = 'the row start offset'
_count_help = 'the number of rows'
_flag_help = 'flags passed to the queries'

def flag_parse(flags_in):
    if not isinstance(flags_in, str):
        return {}

    flags = {}
    types = {
        'int': int,
        'flt': float,
        'str': str,
    }
    for arg in flags_in.split(','):
        arg_split = arg.split('=')
        if len(arg_split) == 1:
            flags[arg] = True
        elif len(arg_split) == 2:
            key, value = arg_split
            flags[key] = value
        else:
            raise Exception('invalid flag')
    return flags



parser = argparse.ArgumentParser(description=_description)
parser.add_argument('db_view', metavar='view', type=str, help=_name_of_view)

parser.add_argument('--file_format', dest='format', type=str, help=_file_format, choices=['csv', 'json'], required=True)
parser.add_argument('--query_offset', dest='query_offset', type=int, help=_offset_help, default=0)
parser.add_argument('--query_count', dest='query_count', type=int, help=_count_help, default=None)
parser.add_argument('--query_flags', dest='flags', action='store', type=flag_parse, help=_flag_help, default='')
parser.add_argument('--query_id', dest='query_id', metavar='lookup_id', type=str, help=_id_lookup_help, default=None)

# required arguments
common.db_flags(parser)
common.debug_flags(parser)
