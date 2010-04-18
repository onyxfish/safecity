from django.conf.urls.defaults import *

from safecity.apps.zeep import views

urlpatterns = patterns('',
    url('^incoming/',
        views.incoming,
        name='zeep_incoming'),
)