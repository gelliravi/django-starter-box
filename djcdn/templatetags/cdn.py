import os

from django import template
from django.conf import settings

from djcdn.models import CDNVersion
from djcdn.conf import settings as app_settings 
from djcdn.storage import Util

register = template.Library()

_latest_ver = CDNVersion.objects.get_latest(is_done=True)

@register.simple_tag
def cdn(path, request=None, type='STATIC'):
    if _latest_ver:
        file_name, file_ext = os.path.splitext(path)
        file_ext = file_ext.lstrip('.')
    
        file_name = Util.format_min_file_name(file_name=file_name, file_ext=file_ext)

        if request and 'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', '').lower():
            file_ext_lower = file_ext.lower()
            com_types = getattr(app_settings, 'CDN_'+type+'_COMPRESSED_TYPES')
            if file_ext_lower in com_types:
                file_name = Util.format_gz_file_name(file_name)

        if type=='STATIC':
            if settings.STATISFILES_STORAGE == 'djcdn.storage.s3.VersionedStaticStorage':
                new_path = '%s%s/%s.%s' % (settings.STATIC_URL, _latest_ver.version_str, file_name, file_ext)
            else:
                new_path = '%s%s.%s' % (settings.STATIC_URL, file_name, file_ext)
            return new_path
        elif type == 'DEFAULT':
            new_path = '%s%s.%s' % (settings.MEDIA_URL, file_name, file_ext)
            return new_path 

    return path

