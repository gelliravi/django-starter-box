from __future__ import unicode_literals

import re 

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import cssmin as cssmin_mod
import slimit as slimit_mod

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.translation import force_text

_CSS_URL_MATCH = re.compile(
    r'(?<!\w)url\([ \t]*(?P<quote>[\'"]?)(?P<url>.*?)(?P=quote)[ \t]*\)|'+
      r'@import[ \t]+(?P<quote1>[\'"]?)(?P<url1>.*?)(?P=quote1)',
    re.IGNORECASE
)

def cssmin(input_file):
    """
    :type   input_file: File 

    :returns: File 
    """

    content_raw = input_file.read()
    output_raw  = cssmin_mod.cssmin(content_raw)

    return ContentFile(output_raw)
 
def _transform_url(url, version_str=None):
    url = url.strip()

    if url.startswith(settings.STATIC_ROOT):
        root_len = len(settings.STATIC_ROOT)

        ver = ''
        if version_str:
            ver = version_str + '/'

        url = settings.STATIC_URL + ver + url[root_len:].lstrip('/')

    return url

def csspath(input_file, version_str=None):
    """
    :type   input_file: File 

    :returns: File   
    """

    input_str = force_text(input_file.read())
    cur = 0
    output = StringIO()
    matches = _CSS_URL_MATCH.finditer(input_str)
    
    for match in matches:
        url = match.group('url')
        if url is None:
            url = match.group('url1')
            start, end = match.span('url1')
        else:    
            start, end = match.span('url')

        output.write(input_str[cur:start])
        output.write(_transform_url(url, version_str=version_str).encode('utf8'))
        cur = end
        
    output.write(input_str[cur:])
    output.seek(0)

    return File(output)

def slimit(input_file):
    """
    :type   input_file: File  

    :returns: File 
    """
    
    content_raw = input_file.read()
    output_raw  = slimit_mod.minify(content_raw, mangle=True, mangle_toplevel=False)
    
    return ContentFile(output_raw)
    
