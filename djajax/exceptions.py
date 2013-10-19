class AjaxError(Exception):
    """
    Root class for all DjAjax related errors.
    """

    pass 

class InvalidMethodError(AjaxError):
    """
    Raised when the called method name is invalid or not registered.
    """

    pass 

class InvalidParamError(AjaxError):
    """
    Raised when one or more params are invalid.
    """

    def __init__(self, errors):
        """
        :type   errors: map
        :param  errors: A map which key is the param's name and the value
            is a list/tuple of error messages. Must be a list/tuple even
            if there is only one error message.        
        """

        self.errors = errors

class InvalidDataError(AjaxError):
    """
    Raised when the input data cannot be JSON decoded.
    """

    pass