import sys

from django.conf import settings

def is_test():
    """ Checks whether Django is running in a test framework. """
    
    return 'test' in sys.argv

class Session(dict):
    """ A limited mock session just for the unit tests in this project. """

    def set_expiry(self, expiry):
        self._expiry = expiry 

    def cycle_key(self):
        pass
