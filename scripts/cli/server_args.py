import argparse
import cli.common_args as common

_description = 'Runs a REST API for the database'
_help_port_arg = 'To specify the port number to run on'

parser = argparse.ArgumentParser(description=_description)
parser.add_argument('port', metavar='port', type=str, help=_help_port_arg)

common.db_flags(parser)
common.debug_flags(parser)
