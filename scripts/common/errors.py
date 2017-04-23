class ThesisError(Exception):
    status_code = 500
    _api_title = "Error"
    _api_message = "Internal Error"
    _code = None

    def __init__(self, message, *args, **kwargs):
        super(ThesisError, self).__init__(message, *args, **kwargs)
        self._message = message

    def format_error(self):
        return {
            'code': self._code,
            'title': self._api_title,
            'detail': self._api_message,
        }

class PopulationError(ThesisError):
    pass

class MissingDBError(PopulationError):
    def __init__(self, *args, **kwargs):
        message = "expected db connection"
        super(MissingDBError, self).__init__(message, *args, **kwargs)

class CorruptDataError(PopulationError):
    def __init__(self, *args, **kwargs):
        message = "data corruption"
        super(CorruptDataError, self).__init__(message, *args, **kwargs)

class InvalidTaskDir(PopulationError):
    def __init__(self, path, *args, **kwargs):
        message = "invalid task dir: '%s'" % path
        super(InvalidTaskDir, self).__init__(message, *args, **kwargs)
        self.task_dir = path

class ArgumentError(PopulationError):
    def __init__(self, arg_name, problem, *args, **kwargs):
        message = "'%s', %s" % (arg_name, problem)
        super(ArgumentError, self).__init__(message, *args, **kwargs)

class NotSpecifiedArg(ArgumentError):
    def __init__(self, arg_name, *args, **kwargs):
        super(NotSpecifiedArg, self).__init__(arg_name, "wasn't specfied", *args, **kwargs)


class IllegalOperation(ThesisError):
    status_code = 500
    _code = 2
    def __init__(self, *args, **kwargs):
        message = "Illegal operation was performed"
        super(IllegalOperation, self).__init__(message, *args, **kwargs)

class APIError(ThesisError):
    pass

class ImmpossibleAcceptType(APIError):
    status_code = 400
    _code = 1
    _api_title = 'Invalid accept header'

    def __init__(self, mimetypes, *args, **kwargs):
        allowed = "only 'application/vnd.api+json' is accepted"
        message = "The following mime type was provided '%s', %s" % (mimetypes, allowed)
        super(ImmpossibleAcceptType, self).__init__(message, *args, **kwargs)
        self._api_message = message

