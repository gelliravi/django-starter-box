class AjaxError(Exception):
    """
    Root class for all DjAjax related errors.

    You may create subclasses based on this.
    """

    def __init__(self, message=None, data=None):
        """
        :param  data: Any data that you wish to attach this AjaxError.
        """

        super(AjaxError, self).__init__(message)

        self.data = data

class AjaxMethodError(AjaxError):
    """
    Raised when the called method name is invalid or not registered.

    This is used internally by DjAjax.
    """

    pass 

class AjaxParamError(AjaxError):
    """
    Raised when one or more params are invalid.

    This is used internally by DjAjax.
    """

    def __init__(self, errors):
        """
        :type   errors: map
        :param  errors: A map which key is the param's name and the value
            is a list/tuple of error messages. Must be a list/tuple even
            if there is only one error message. The blank key represents
            errors not tied to any field. 
        """

        super(AjaxParamError, self).__init__(data=errors)

class AjaxDataError(AjaxError):
    """
    Raised when the input data cannot be JSON decoded.

    This is used internally by DjAjax.
    """

    pass