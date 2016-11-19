class AnalysisError(Exception):
    pass

class MissingDBError(AnalysisError):
    def __init__(self, *args, **kwargs):
        message = "expected db connection"
        super(MissingDBError, self).__init__(message, *args, **kwargs)

class CorruptDataError(AnalysisError):
    def __init__(self, *args, **kwargs):
        message = "data corruption"
        super(CorruptDataError, self).__init__(message, *args, **kwargs)

class InvalidTaskDir(AnalysisError):
    def __init__(self, path, *args, **kwargs):
        message = "invalid task dir: '%s'" % path
        super(InvalidTaskDir, self).__init__(message, *args, **kwargs)
        self.task_dir = path

class ArgumentError(AnalysisError):
    def __init__(self, arg_name, problem, *args, **kwargs):
        message = "'%s', %s" % (arg_name, problem)
        super(ArgumentError, self).__init__(message, *args, **kwargs)

class NotSpecifiedArg(ArgumentError):
    def __init__(self, arg_name, *args, **kwargs):
        super(NotSpecifiedArg, self).__init__(arg_name, "wasn't specfied", *args, **kwargs)



