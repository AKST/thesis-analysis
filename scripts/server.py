import logging
from flask import Flask, request, g
from format import from_db
from io import StringIO

from data.models.script import Script
from data.models.package import Package
from data.models.results import ResultsAPI

app = Flask("thesis")

class DataQuery:
    def __init__(self, flags, format='json', query_id=None):
        self.flags = flags
        self.format = format
        self.query_id = query_id
        self.query_count = None
        self.query_offset = None

def query_model(Model, query):
    buffer = StringIO()
    query.query_count = request.args.get('count', None)
    query.query_offset = request.args.get('offset', None)
    from_db(Model, g.db_connection, buffer, query)
    return buffer.getvalue()

@app.route("/packages", methods=["GET"])
def get_packages():
    query = DataQuery({})
    return query_model(Package, query)

@app.route("/packages/<id>", methods=["GET"])
def get_package(id=None):
    query = DataQuery({}, query_id=id)
    return query_model(Package, query)

@app.route("/scripts", methods=["GET"])
def get_scripts():
    flags = {}
    flags['with_repr'] = 'with_repr' in request.args
    query = DataQuery(flags)
    return query_model(Script, query)

@app.route("/scripts/<id>", methods=["GET"])
def get_script(id=None):
    flags = {}
    flags['with_repr'] = 'with_repr' in request.args
    query = DataQuery(flags, query_id=id)
    return query_model(Script, query)

@app.route("/results", methods=["GET"])
def get_results():
    flags = {}
    flags['O'] = 2
    flags['avg'] = True
    flags['file_extension'] = request.args.get('file_extension', None)
    return query_model(ResultsAPI, DataQuery(flags))


if __name__ == '__main__':
    from data.connect import pg_connection
    from cli.config import setup_logging
    from cli.server_args import parser as arg_parser

    args = arg_parser.parse_args()
    setup_logging(args)
    logging.debug("args: %s", args)

    @app.after_request
    def close_db(response):
        g.db_connection.close()
        return response

    @app.before_request
    def setup_db():
        g.db_connection = pg_connection(args)

    app.run(port=args.port)
