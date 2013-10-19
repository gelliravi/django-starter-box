from django.http import HttpResponse
from djbase.utils.json import encode as json_encode

from . import djajax 
from .exceptions import *

import json

def _ajax_json(error=None, data=None):
    """
    :type   error: Exception 
    """

    error_dict = None

    if error:
        error_dict = {
            'type':     error.__class__.__name__,
        }

        if isinstance(error, AjaxError):
            error_dict['message'] = str(error)             

            if isinstance(error, InvalidParamError):
                error_dict['data'] = error.errors

    return json_encode({'error': error_dict, 'data': data})

def _ajax_response(error=None, data=None):
    return HttpResponse(_ajax_json(error=error, data=data), content_type='application/json')

def call(request, name):
    """
    Handles AJAX calls. 

    It accepts a single 'data' param which is a JSONinified version of the
    input data.
    """

    try:
        entry = djajax.get(name=name, method=request.method)
        if not entry:
            raise InvalidMethodError()

        data_raw = getattr(request, request.method).get('data', None)
        if data_raw is None:
            data = {}
        else:
            try:
                data = json.loads(data_raw)
            except (ValueError, TypeError):
                raise InvalidDataError()

        if entry.form:
            form = entry.form(data)
            is_valid = form.is_valid()
            if not is_valid:
                raise InvalidParamError(errors=form.errors)

            data = form.cleaned_data

        output = entry.call(request=request, params=data)

        return _ajax_response(data=output)

    except Exception as e:
        return _ajax_response(error=e)
