from django.conf.urls.defaults import *

from safecity.apps.public import views

urlpatterns = patterns('',
    url('^$',
        views.index,
        name='public_index'),
)