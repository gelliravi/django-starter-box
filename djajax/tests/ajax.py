from django import forms
from djbase.forms import ISODateTimeField
from djajax.decorators import djajax 

class PostForm(forms.Form):
    param1  = ISODateTimeField(required=False)
    param2  = forms.CharField(max_length=5, required=True)

@djajax(method='POST')
def post_no_param(request):
    return 'success'

@djajax(method='POST')
def post_with_params(request, param1, param2):
    return {
        'param1'    : param1,
        'param2'    : param2,
    }

@djajax(method='POST', form=PostForm)
def post_with_form_params(request, param1, param2):
    return {
        'param1'    : param1,
        'param2'    : param2,
    }

@djajax(method='GET', form=PostForm)
def get_with_form_params(request, param1, param2):
    return {
        'param1'    : param1,
        'param2'    : param2,
    }

@djajax(name='multi.post', method='POST')
@djajax(name='multi.get', method='GET')
def multi(request):
    return 'success'
