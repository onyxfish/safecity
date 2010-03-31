from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()
admin.site.disable_action('delete_selected')

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT
    }),
)