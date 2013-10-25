from __future__ import unicode_literals

import hashlib

from django.conf import settings as django_settings

def _hash(s):
    m = hashlib.sha1()
    m.update(s)
    hash = m.hexdigest().lower()

    m = hashlib.sha1()
    m.update(s + hash)
    return m.hexdigest().lower()

class _Settings(object):
    DEFAULTS = {
        'ACCOUNT_LOWER_EMAIL'                       :   True,
        'ACCOUNT_PASSWORD_RESET_EXPIRY_MINUTES'     :   120,
        'ACCOUNT_PASSWORD_RESET_THRESHOLD_MINUTES'  :   10,
        'ACCOUNT_SECRET_KEY'                        :   _hash(django_settings.SECRET_KEY)
    }

    def __getattr__(self, name):
        def_val = self.DEFAULTS.get(name, None)

        if def_val is not None:
            return getattr(django_settings, name, def_val)

        return def_val

    @property 
    def is_test(self):
        import sys
        return 'test' in sys.argv

settings = _Settings()