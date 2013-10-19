from django.conf.urls import patterns, include, url

from djajax.core import djajax_autodiscover

djajax_autodiscover()

urlpatterns = patterns('',
    url(r'^djajax/', include('djajax.urls')),
)