import os

from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from djcdn.models import CDNVersion
from djcdn.conf import settings as app_settings 
from djcdn.storage import Util

register = template.Library()

_latest_ver     = CDNVersion.objects.get_latest(is_done=True)
_static_storage = settings.STATICFILES_STORAGE 
_is_versioned   = _static_storage == 'djcdn.storage.s3.VersionedStaticStorage'
_is_static      = _static_storage == 'djcdn.storage.s3.StaticStorage'

@register.simple_tag(takes_context=True)
def cdn(context, path, type='STATIC'):
    global _static_storage, _latest_ver, _is_versioned, _is_static 

    request = context['request']

    file_name, file_ext = os.path.splitext(path)
    file_ext = file_ext.lstrip('.')

    file_name = Util.format_min_file_name(file_name=file_name, file_ext=file_ext)

    if 'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', '').lower():
        file_ext_lower = file_ext.lower()
        com_types = getattr(app_settings, 'CDN_'+type+'_COMPRESSED_TYPES')
        if file_ext_lower in com_types:
            file_name = Util.format_gz_file_name(file_name)

    if type=='STATIC':
        if _latest_ver and _is_versioned:
            new_path = '%s%s/%s.%s' % (settings.STATIC_URL, _latest_ver.version_str, file_name, file_ext)
        elif _is_static:
            new_path = '%s%s.%s' % (settings.STATIC_URL, file_name, file_ext)
        else:
            # fallback to original staticfiles behavior
            new_path = staticfiles_storage.url(path) 
        return new_path
    elif type == 'DEFAULT':
        new_path = '%s%s.%s' % (settings.MEDIA_URL, file_name, file_ext)
        return new_path 

    return path 
