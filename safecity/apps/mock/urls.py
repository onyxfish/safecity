from django.conf.urls.defaults import *

from safecity.apps.mock import views

urlpatterns = patterns('',
    url('^$',
        views.mock,
        name='mock'),
)