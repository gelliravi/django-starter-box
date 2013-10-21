from django import forms
from djbase.forms import ISODateTimeField
from djajax.decorators import ajax 
from djajax.exceptions import AjaxError

class PostForm(forms.Form):
    param1  = ISODateTimeField(required=False)
    param2  = forms.CharField(max_length=5, required=True)

class EmailTakenError(AjaxError):
    """
    Custom error that represents the registering email is already used.
    """

    pass

class UserNameTakenError(AjaxError):
    """
    Custom error that represents the username is already taken.
    """

    def __init__(self, suggestions):
        super(UserNameTakenError, self).__init__(
            message='The username you chosen has been taken. Here are some suggestions.', 
            data=suggestions)

@ajax(method='POST')
def post_no_param(request):
    return 'success'

@ajax(method='POST')
def post_with_params(request, param1, param2):
    return {
        'param1'    : param1,
        'param2'    : param2,
    }

@ajax(method='POST', form=PostForm)
def post_with_form_params(request, param1, param2):
    return {
        'param1'    : param1,
        'param2'    : param2,
    }

@ajax(method='POST')
def create_account(request):
    raise EmailTakenError()

@ajax(method='POST')
def create_account_2(request, username):
    raise UserNameTakenError(suggestions=('suggested1', 'suggested2'))

@ajax(method='GET', form=PostForm)
def get_with_form_params(request, param1, param2):
    return {
        'param1'    : param1,
        'param2'    : param2,
    }

@ajax(name='multi.post', method='POST')
@ajax(name='multi.get', method='GET')
def multi(request):
    return 'success'
