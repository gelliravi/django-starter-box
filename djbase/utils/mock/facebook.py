"""
Mock Facebook for Python. Sufficient for the tests in this project.
"""

_ACCESS_TOKEN = '123456789abcdef' * 5

PROFILE = {
    'email'         : 'john@doe.com',
    'first_name'    : 'John',
    'middle_name'   : 'Middle',
    'last_name'     : 'Doe',
    'name'          : 'John Doe',
    'gender'        : 'male',
    'age_range'     : {'min': 17, 'max': 21},
    'locale'        : 'en_US',
    'timezone'      : 8.0,
    'friends'       : {
        'data':     ({'id': '1000123789'},{'id': '1000123788'})
    },
}
        
def get_user_from_cookie(cookies, app_id, app_secret):
    return {
        'uid'           : '1000123456',
        'access_token'  : _ACCESS_TOKEN
    }

class GraphAPI(object):
    def __init__(self, access_token=None, timeout=None):
        self.access_token = access_token
        self.timeout = timeout
        
    def request(self, path, args=None, post_args=None):
        global PROFILE

        if self.access_token != _ACCESS_TOKEN:
            raise Exception('Invalid Access Token')

        if path == '/me' or path == 'me':
            fields = args['fields'].split(',')
            ret = {}
            for f in fields:
                v = PROFILE.get(f, None)
                if v is not None:
                    ret[f] = v 

            if 'friends.id' in fields:
                ret['friends'] = PROFILE['friends']

            return ret
        else:
            raise Exception('not supported path: '+path)
    
    def get_object(self, id, **kwargs):
        return self.request(path=id, args=kwargs)
        
        