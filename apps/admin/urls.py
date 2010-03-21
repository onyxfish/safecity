from django.conf.urls.defaults import *
from django.contrib.gis import admin

admin.autodiscover()
admin.site.disable_action('delete_selected')
 
urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
)
