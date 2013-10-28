from __future__ import unicode_literals

from datetime import datetime, timedelta
import inspect

from django.core.files import File
from django.core.files.base import ContentFile 

from djcdn import filters as filters_mod

class Util(object):
    # locale independent... the GMT format should just be pure numbers.
    DAYS    = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

    MONTHS  = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
               'Sep', 'Oct', 'Nov', 'Dec')

    @classmethod
    def get_expiry_headers(cls, age):
        """
        Get Expires and Cache-Control headers.

        :type   age: int 
        :param  age: Expiry age in seconds. 

        :returns:   dict 
        """

        days = cls.DAYS 
        months = cls.MONTHS 

        now = datetime.utcnow()
        expires = now + timedelta(seconds=age)
        expires_str = expires.strftime('%%s, %d %%s %Y %H:%M:%S GMT')
        expires_str = expires_str % (days[expires.weekday()], months[expires.month-1])
        headers = {
            'Expires'       : expires_str,
            'Cache-Control' : 'public, max-age=%s' % age, 
        }

        return headers

    @classmethod
    def delete_file(cls, file):
        if isinstance(file, ContentFile) or not hasattr(file, 'delete') or not file.name:
            return 

        try:
            file.delete()
        except Exception as e:
            print('Warning: Cannot delete temp file (Reason: %s): %s' 
                % (e, file.name))

    @classmethod 
    def _call_filter(cls, filter_fn, input_file, version_str):
        argspec = inspect.getargspec(filter_fn)

        if 'version_str' in argspec.args:
            return filter_fn(input_file=input_file, version_str=version_str)

        return filter_fn(input_file=input_file)

    @classmethod
    def apply_filters(cls, filters, input_file, version_str=None):
        """
        :type   input_file: File
        :param  input_file: Will start reading at the current file position.

        :returns: 
            File -- may be the same as input_file. 
            File position indeterminate.
        """
        
        output_file = input_file
        is_first = True 

        for filter in filters:
            if not filter.startswith('filters.'):
                continue 

            fn_name = filter.split('.')[1]
            filter_fn = getattr(filters_mod, fn_name, None)
            
            if filter_fn is None:
                raise Exception('filter function does not exist: %s' % filter)

            new_output_file = cls._call_filter(filter_fn, input_file=output_file, version_str=version_str)

            # Delete intermediate files
            if (not is_first) and not(output_file is new_output_file):
                output_file.close()
                cls.delete_file(output_file)

            is_first = False 
            output_file = new_output_file

        return output_file

    @classmethod 
    def can_minify(cls, file_ext):
        return file_ext.lower() in ('css', 'js')

    @classmethod 
    def format_min_file_name(cls, file_name, file_ext):
        if cls.can_minify(file_ext):
            return '%s.min' % file_name 
        return file_name 

    @classmethod 
    def format_gz_file_name(cls, file_name):
        return '%s.gz' % file_name 
