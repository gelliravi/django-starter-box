from django.utils.importlib import import_module

_LOADING = False

def _clean_method(method):
    method = method.strip().upper()

    if method in ['POST', 'GET']:
        return method 

    return 'POST'

def djajax_autodiscover():
    """
    Auto-discover INSTALLED_APPS ajax.py modules and fail silently when
    not present. NOTE: This is inspired/copied from dajaxice_autodiscover.
    """

    global _LOADING

    if _LOADING:
        return

    _LOADING = True

    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('ajax', app_path)
        except ImportError:
            continue

        import_module("%s.ajax" % app)

class DjAjaxEntry(object):
    def __init__(self, name, method, function):
        self.name = name
        self.method = method
        self.function = function
        
    def call(self, *args, **kwargs):
        """ Call the function. """
        
        return self.function(*args, **kwargs)

class DjAjax(object):
    def __init__(self):
        self._entries = {}

    def register(self, function, name=None, method='POST'):
        """
        Register a function as an AJAX method.

        If no name is provided, the module and the function name will be used.
        The final (customized or not) must be unique. 
        """

        method = _clean_method(method)

        # Generate a default name
        if not name:
            module = ''.join(str(function.__module__).rsplit('.ajax', 1))
            name = '.'.join((module, function.__name__))

        if ':' in name:
            raise Exception('Invalid AJAX method name: %s' % name)

        if name in self._entries:
            raise Exception('AJAX method already registered: %s' % name)

        entry = DjAjaxEntry(name=name, method=method, function=function)
        self._entries[name] = entry