import json
from argparse import Action

_db_name_help = 'Name of the database'
_db_host_help = 'Hostname for database'
_db_user_help = 'Username for database'
_db_pass_help = 'Password for database'
_db_conf_help = 'File with db configurations'
_log_level_help = 'logging level'
_log_format_help = 'formatting for logs'
_default_log_format = '[%(levelname)s %(asctime)s] :: %(message)s'

class _DBConfAction(Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError('cannot override nargs for --db-conf')
        super(_DBConfAction, self).__init__(option_strings, dest, nargs=1, type=str, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 1:
            raise ValueError('multiple config files specified')

        file_name = values[0]
        with open(file_name) as f:
            conf = json.load(f)
            setattr(namespace, 'db_host', conf['db-host'])
            setattr(namespace, 'db_name', conf['db-name'])
            setattr(namespace, 'db_user', conf['db-user'])
            setattr(namespace, 'db_pass', conf['db-pass'])


def db_flags(parser):
    parser.add_argument('--db-name', dest='db_name', default='thesis-data', help=_db_name_help)
    parser.add_argument('--db-host', dest='db_host', default='localhost', help=_db_host_help)
    parser.add_argument('--db-user', dest='db_user', default='postgres', help=_db_user_help)
    parser.add_argument('--db-pass', dest='db_pass', default='', help=_db_pass_help)
    parser.add_argument('--db-conf', default=None, help=_db_conf_help, action=_DBConfAction)

def debug_flags(parser):
    parser.add_argument('--log-level', dest='log_level', default='ERROR', help=_log_level_help)
    parser.add_argument('--log-format', dest='log_format', default=_default_log_format, help=_log_format_help)

