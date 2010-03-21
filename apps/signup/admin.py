from django.contrib.gis import admin

from apps.signup.models import *

class ResidentAdmin(admin.OSMGeoAdmin):
    # Basic admin config
    fields = ('phone_number', 'location')
    list_display = ('phone_number',)
    readonly_fields = ('phone_number',)
    search_fields = ('=phone_number',)
    
    # Geo admin config
    point_zoom = 16
    modifiable = False    # TODO - doesn't hide "Delete all Features" link under map

admin.site.register(Resident, ResidentAdmin)