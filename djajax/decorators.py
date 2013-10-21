import functools

from . import ajax_core 

def ajax(*args, **kwargs):
    """ 
    Register some function as an AJAX method.
    """

    if len(args) and not kwargs:
        function = args[0]
        ajax_core.register(function)
        return function

    def decorator(function):
        @functools.wraps(function)
        def wrapper(request, *args2, **kwargs2):
            return function(request, *args2, **kwargs2)

        ajax_core.register(function, *args, **kwargs)
        return wrapper

    return decorator