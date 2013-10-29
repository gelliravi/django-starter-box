from __future__ import unicode_literals

from django.conf import settings as django_settings

class _Settings(object):
    DEFAULTS = {
        'CDN_STATIC_COMPRESSED_TYPES'        : ('css', 'js'), # Lowercase
        'CDN_DEFAULT_COMPRESSED_TYPES'       : (),

        'CDN_STATIC_FILTERS'               : {
            'css'   : ('filters.cssmin', 'filters.csspath'),
            'js'    : ('filters.slimit',),
            'png'   : ('filters.pngcrush',),
            'jpg'   : ('filters.jpegoptim',),
            'jpeg'  : ('filters.jpegoptim',),
        },
        'CDN_DEFAULT_FILTERS'               : {
            # none
        },

        'CDN_STATIC_EXPIRY_AGE'      : 3600 * 24 * 365, # seconds
        'CDN_DEFAULT_EXPIRY_AGE'     : 3600 * 24 * 365, # seconds
    }

    def __getattr__(self, name):
        def_val = self.DEFAULTS.get(name, None)

        if def_val is not None:
            return getattr(django_settings, name, def_val)

        return def_val

settings = _Settings()
