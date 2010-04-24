from django.conf.urls.defaults import *

from safecity.apps.tropo import views

urlpatterns = patterns('',
    url('^incoming/',
        views.incoming,
        name='tropo_incoming'),
)