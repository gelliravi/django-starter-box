from django.conf import settings

class Session(dict):
    """ A limited mock session just for the unit tests in this project. """

    def set_expiry(self, expiry):
        self._expiry = expiry 

    def cycle_key(self):
        pass
