from django.conf.urls.defaults import *

import apps.logger.views as views

urlpatterns = patterns('',
    url(r'^logger/?$', views.index),
)
