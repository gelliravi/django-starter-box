from __future__ import unicode_literals

import os
import sys
import mimetypes

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO  

from storages.backends.s3boto import S3BotoStorage
from django.conf import settings

from djcdn.models import CDNVersion
from djcdn.conf import settings as app_settings
from djcdn.storage import Util

class AbstractStorage(S3BotoStorage):
    """
    Base storage for S3.
    """

    def __init__(self, cdn_type, *args, **kwargs):
        self._parent = super(AbstractStorage, self)
        self._cdn_type = cdn_type 

        aws_headers = getattr(settings, 'AWS_HEADERS', {})
        headers = aws_headers.copy()
        
        age = self._cdn_settings('EXPIRY_AGE')
        if age > 0: 
            expiry_headers = Util.get_expiry_headers(age=age)
            headers.update(expiry_headers)

        gzip_types = list(getattr(settings, 'GZIP_CONTENT_TYPES', ()))
        com_types = self._cdn_settings('COMPRESSED_TYPES')
        for type in com_types:
            mime = mimetypes.types_map.get('.'+type, None)
            if mime:
                gzip_types += (mime,)
            
        self._cdn_gzip_storage =  S3BotoStorage(*args, headers=headers, gzip=True, gzip_content_types=gzip_types, **kwargs)
        self._parent.__init__(*args, headers=headers, gzip=False, **kwargs)

    def url(self, name):
        """
        fix the broken javascript admin resources with S3Boto on Django 1.4
        for more info see http://code.larlet.fr/django-storages/issue/121/s3boto-admin-prefix-issue-with-django-14

        This is taken from django-s3-folder-storage. Credits go to the author.
        """

        url = self._parent.url(name)
        if name.endswith('/') and not url.endswith('/'):
            url += '/'
        return url

    def _cdn_settings(self, name):
        return getattr(app_settings, 'CDN_%s_%s' % (self._cdn_type, name))

    def _save(self, name, content):
        orig_content = content 

        file_name, file_ext = os.path.splitext(name)
        file_ext = file_ext.lstrip('.')
        file_ext_lower = file_ext.lower()
        
        filters_map = self._cdn_settings('FILTERS')
        filters = filters_map.get(file_ext_lower, None)

        content_raw = None 
        new_name =  name 
            
        if filters:
            content_raw = Util.apply_filters(filters=filters, content=content.read())
            file_name = Util.format_min_file_name(file_name, file_ext)
            new_name = '%s.%s' % (file_name, file_ext)
            content.file = StringIO(content_raw)
            
        self._parent._save(name=new_name, content=content,)
        
        if file_ext in self._cdn_settings('COMPRESSED_TYPES'):
            content.seek(0)

            # must preserve file ext!
            gzip_file_name = Util.format_gz_file_name(file_name)
            gzip_name = '%s.%s' % (gzip_file_name, file_ext)
            self._cdn_gzip_storage._save(name=gzip_name, content=content,)

        return new_name 

class StaticStorage(AbstractStorage):
    """
    Storage for static files.
    The folder is defined in settings.CDN_STATIC_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        if not 'location' in kwargs:
            kwargs['location'] = settings.CDN_STATIC_S3_PATH
        super(StaticStorage, self).__init__(*args, cdn_type='STATIC', **kwargs)

class DefaultStorage(AbstractStorage):
    """
    Storage for uploaded media files.
    The folder is defined in settings.CDN_DEFAULT_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.CDN_DEFAULT_S3_PATH
        super(DefaultStorage, self).__init__(*args, cdn_type='DEFAULT', **kwargs)

class VersionedStaticStorage(StaticStorage):
    def __init__(self, *args, **kwargs):
        if 'collectstatic' in sys.argv:
            version_str = CDNVersion.objects.create_new().version_str + '/'
        else:
            version_str = ''

        location = settings.CDN_STATIC_S3_PATH + version_str

        self._parent = super(VersionedStaticStorage, self)
        self._parent.__init__(*args, location=location, **kwargs)
