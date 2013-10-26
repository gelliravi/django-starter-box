from datetime import datetime, timedelta

from djcdn import filters as filters_mod

class Util(object):
    # locale independent... the GMT format should just be pure numbers.
    DAYS    = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

    MONTHS  = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
               'Sep', 'Oct', 'Nov', 'Dec')

    @classmethod
    def get_expiry_headers(cls, age):
        """
        Get Expries and Cache-Control headers.

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
    def apply_filters(cls, filters, content):
        """
        :type   content: str

        :returns: str   
        """
        
        for filter in filters:
            if not filter.startswith('filters.'):
                continue 

            fn_name = filter.split('.')[1]
            filter_fn = getattr(filters_mod, fn_name, None)
            
            if filter_fn is None:
                raise Exception('filter function does not exist: %s' % fn_name)

            content = filter_fn(content=content)

        return content

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
