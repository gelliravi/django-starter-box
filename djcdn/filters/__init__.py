from __future__ import unicode_literals

import cssmin as cssmin_mod
import slimit as slimit_mod

from django.core.files import File
from django.core.files.base import ContentFile

def cssmin(input_file):
    """
    :type   input_file: File 

    :returns: File 
    """

    content_raw = input_file.read()
    output_raw  = cssmin_mod.cssmin(content_raw)

    return ContentFile(output_raw)
 
def csspath(input_file):
    """
    :type   input_file: File 

    :returns: File   
    """
    
    # TODO rewrite url(xxx) and @import url(xxx)
    return input_file

def slimit(input_file):
    """
    :type   input_file: File  

    :returns: File 
    """
    
    content_raw = input_file.read()
    output_raw  = slimit_mod.minify(content_raw, mangle=True, mangle_toplevel=False)
    
    return ContentFile(output_raw)
    
