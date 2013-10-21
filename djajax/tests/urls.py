from django.conf.urls import patterns, include, url

from djajax.core import ajax_autodiscover

ajax_autodiscover()

urlpatterns = patterns('',
    url(r'^djajax/', include('djajax.urls')),
)