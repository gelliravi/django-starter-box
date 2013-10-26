from django import template
from django.conf import settings

from djcdn.models import CDNVersion
from djcdn.conf import settings as app_settings 

register = template.Library()

_latest_ver = CDNVersion.objects.get_latest(is_done=True)

@register.simple_tag
def cdn(path, type='STATIC'):
    if _latest_ver:
        file_name, file_ext = os.path.splitext(path)
        file_ext = file_ext.lstrip('.')
    
        file_name = Util.format_min_file_name(file_name=file_name, file_ext=file_ext)

        com_types = getattr(app_settings, 'CDN_'+type+'_COMPRESSED_TYPES')
        if file_ext_lower in com_types:
            file_name = Util.format_gz_file_name(file_name)

        new_path = '%s/%s.%s' % (_latest_ver.version_str, file_name, file_ext)
        return  settings.STATIC_URL + new_path 

    return path

