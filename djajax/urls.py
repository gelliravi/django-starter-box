from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<name>.*)$', 
        views.call, 
        name='call'),
)