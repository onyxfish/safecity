from django.contrib.gis import admin

from apps.locate.models import *

admin.site.register(Road, admin.OSMGeoAdmin)
admin.site.register(RoadAlias)
admin.site.register(Intersection, admin.OSMGeoAdmin)
admin.site.register(Block, admin.OSMGeoAdmin)
admin.site.register(Landmark, admin.OSMGeoAdmin)
admin.site.register(LandmarkAlias)