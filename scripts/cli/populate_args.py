import argparse
import cli.common_args as common

_description = 'Populates database with data from benchmarking output'
_data_folder_help = 'the folder which will be recursed to read data from'
_config_file_help = 'meta data file of packages which have been benchmarked'


parser = argparse.ArgumentParser(description=_description)

# required arguments
parser.add_argument('data_folder', metavar='data', type=str, help=_data_folder_help)
parser.add_argument('config_file', metavar='meta', type=str, help=_config_file_help)
common.db_flags(parser)
common.debug_flags(parser)
