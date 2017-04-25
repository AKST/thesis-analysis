import logging
from flask import Flask, request, g, jsonify
from io import StringIO
from uuid import uuid4

from format import from_db
import common.errors as errors
from data.models.script import Script
from data.models.package import Package
from data.models.filetype import FileType
from data.models.results import ResultsAPI

app = Flask("thesis")

_JSON_API_CONTENT_TYPE = 'application/vnd.api+json'

class DataQuery:
    def __init__(self, flags, query_id=None):
        self.flags = flags
        self.format = 'json'
        self.query_id = query_id
        self.query_count = None
        self.query_offset = None

def query_model(Model, query):
    buffer = StringIO()
    query.query_count = request.args.get('count', None)
    query.query_offset = request.args.get('offset', None)
    from_db(Model, g.db_connection, buffer, query)
    return buffer.getvalue()

@app.errorhandler(404)
def url_not_found(error):
    return format_error(errors.LocationNotFound())

@app.errorhandler(errors.ThesisError)
def format_error(error):
    logging.error("REQUEST: %s ERROR: %s" % (g.request_id, error))
    response = jsonify({
        'jsonapi': { 'version': '1.0' },
        'errors': [error.format_error()],
    })
    response.status_code = error.status_code
    return response

@app.errorhandler(Exception)
def handle_unknown_error(error):
    return format_error(errors.InternalError(error))

@app.route("/api/v0/packages", methods=["GET"])
def get_packages():
    query = DataQuery({})
    return query_model(Package, query)

@app.route("/api/v0/packages/<id>", methods=["GET"])
def get_package(id=None):
    query = DataQuery({}, query_id=int(id))
    return query_model(Package, query)

@app.route("/api/v0/scripts", methods=["GET"])
def get_scripts():
    flags = {}
    flags['with_repr'] = 'with_repr' in request.args
    query = DataQuery(flags)
    return query_model(Script, query)

@app.route("/api/v0/filetypes", methods=["GET"])
def get_filetypes():
    query = DataQuery({})
    return query_model(FileType, query)

@app.route("/api/v0/scripts/<id>", methods=["GET"])
def get_script(id=None):
    flags = {}
    flags['with_repr'] = 'with_repr' in request.args
    query = DataQuery(flags, query_id=id)
    return query_model(Script, query)

@app.route("/api/v0/results", methods=["GET"])
def get_results():
    flags = {}
    flags['O'] = 2
    flags['avg'] = True
    flags['file_extension'] = request.args.get('fileExtension', None)
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
        if hasattr(g, 'db_connection'):
            g.db_connection.close()
        response.headers["Content-Type"] = _JSON_API_CONTENT_TYPE
        return response

    @app.before_request
    def setup_request():
        g.request_id = uuid4()
        user_agent = request.headers.get('User-Agent')
        message = "REQUEST: %s IP: %s USER-AGENT: %s" % (g.request_id, request.remote_addr, user_agent)
        logging.info(message)
        accepts = request.headers.get('Accept', '')
        if accepts == _JSON_API_CONTENT_TYPE:
            g.db_connection = pg_connection(args)
        else:
            raise errors.ImmpossibleAcceptType(accepts)

    app.run(port=args.port)
