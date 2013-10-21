class BaseError(Exception):
    def __init__(self, message=None, cause=None):
        self.cause = cause 
        super(BaseError, self).__init__(message)
        