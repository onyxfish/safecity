from django.conf.urls.defaults import *

from safecity.apps.mock import views

urlpatterns = patterns('',
    url('^$',
        views.mock,
        name='mock'),
    url('^sms_ajax$',
        views.mock_sms_ajax,
        name='mock_sms_ajax'),
)