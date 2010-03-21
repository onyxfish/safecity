from django.contrib.gis import admin

from apps.danger.models import *

class ReportAdmin(admin.OSMGeoAdmin):
    # Basic admin config
    date_hierarchy = 'received'
    fields = ('sender', 'text', 'location')
    list_display = ('received', 'sender', 'text')
    readonly_fields = ('sender', 'text')
    search_fields = ('=sender', 'text')
    
    # Geo admin config
    point_zoom = 16
    modifiable = False    # TODO - doesn't hide "Delete all Features" link under map

admin.site.register(Report, ReportAdmin)