from django.contrib.gis import admin

from apps.locate.models import *

admin.site.register(Road)
admin.site.register(RoadAlias)
admin.site.register(Intersection)
admin.site.register(Block)
admin.site.register(Landmark)
admin.site.register(LandmarkAlias)