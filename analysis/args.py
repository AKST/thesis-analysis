import argparse

_description = 'Populates database with data from benchmarking output'
_data_folder_help = 'the folder which will be recursed to read data from'
_config_file_help = 'meta data file of packages which have been benchmarked'
_db_name_help = 'Name of the database'
_db_host_help = 'Hostname for database'
_db_user_help = 'Username for database'
_db_pass_help = 'Password for database'
_log_level_help = 'logging level'
_log_format_help = 'formatting for logs'

_default_log_format = '[%(levelname)s %(asctime)s] :: %(message)s'

parser = argparse.ArgumentParser(description=_description)

# required arguments
parser.add_argument('data_folder', metavar='data', type=str, help=_data_folder_help)
parser.add_argument('config_file', metavar='meta', type=str, help=_config_file_help)

# database arguments
parser.add_argument('--db-name', dest='db_name', default='thesis-data', help=_db_name_help)
parser.add_argument('--db-host', dest='db_host', default='localhost', help=_db_host_help)
parser.add_argument('--db-user', dest='db_user', default='postgres', help=_db_user_help)
parser.add_argument('--db-pass', dest='db_pass', default='', help=_db_pass_help)

parser.add_argument('--log-level', dest='log_level', default='ERROR', help=_log_level_help)
parser.add_argument('--log-format', dest='log_format', default=_default_log_format, help=_log_format_help)

