from __future__ import unicode_literals

import re 
import os.path
import subprocess
import shutil
import tempfile

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

    content_bytes = input_file.read()
    output_bytes  = cssmin_mod.cssmin(content_bytes)

    return ContentFile(output_bytes)
 
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
    
    content_bytes = input_file.read()
    output_bytes  = slimit_mod.minify(content_bytes, mangle=True, mangle_toplevel=False)
    
    return ContentFile(output_bytes)
    
def jpegoptim(input_file):
    file_path = getattr(input_file,'name', None)
    if not file_path:
        # We need a real file due to the work jpegoptim works.
        print('ERROR: JPEG file has no filename')
        return input_file

    if not os.path.isfile(file_path):
        print('ERROR: JPEG file does not exist: %s' % file_path)
        return input_file 

    tmp_path = tempfile.mkdtemp()
    subprocess.call(["jpegoptim", "--strip-all", file_path, '-d', tmp_path])

    file_name = os.path.basename(file_path)
    old_out_path = os.path.join(tmp_path, file_name)

    if not os.path.isfile(old_out_path):
        print('ERROR: JPEG output file does not exist: %s' % out_path)
        return input_file 

    #
    # Move the output file to a new temp file so we can remove the temp dir.
    #
    (out_handle, out_path) = tempfile.mkstemp(text=False)

    os.rename(old_out_path, out_path)
    os.rmdir(tmp_path)

    return File(open(out_path, 'rb'))

def pngcrush(input_file):
    file_path = getattr(input_file,'name', None)
    if not file_path:
        # We need a real file due to the work jpegoptim works.
        print('ERROR: PNG file has no filename')
        return input_file

    if not os.path.isfile(file_path):
        print('ERROR: PNG file does not exist: %s' % file_path)
        return input_file 

    (out_handle, out_path) = tempfile.mkstemp(text=False)

    # make the tool quiet as it makes too much noise :)
    subprocess.call(["pngcrush", '-q', "-brute", '-reduce', file_path, out_path])

    if not os.path.isfile(out_path):
        print('ERROR: PNG output file does not exist: %s' % out_path)
        return input_file 
        
    return File(open(out_path, 'rb'))
