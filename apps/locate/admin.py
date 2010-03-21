from django.contrib.gis import admin

from apps.locate.models import *

class RoadAdmin(admin.OSMGeoAdmin):
    # Basic admin config
    fields = ('prefix_direction', 'name', 'road_type', 'suffix_direction')
    list_display = ('prefix_direction', 'name', 'road_type', 'suffix_direction')
    list_display_links = ('name',)
    readonly_fields = ('prefix_direction', 'name', 'road_type', 'suffix_direction')
    search_fields = ('=prefix_direction', 'name', '=road_type', '=suffix_direction')
    
    # Geo admin config
    point_zoom = 16
    modifiable = False    # TODO - doesn't hide "Delete all Features" link under map

class BlockAdmin(admin.OSMGeoAdmin):
    # Basic admin config
    fields = ('number', 'road', 'location')
    list_display = ('number', 'road')
    list_display_links = ('number', 'road')
    readonly_fields = ('number', 'road')
    search_fields = ('=number', 'road')

    # Geo admin config
    point_zoom = 16
    modifiable = False    # TODO - doesn't hide "Delete all Features" link under map

class IntersectionAdmin(admin.OSMGeoAdmin):
    # TODO - make this better: inline with Road?
    # Basic admin config
    fields = ('roads', 'location')
    readonly_fields = ('roads',)
    search_fields = ('=roads__prefix_direction', 'roads__name', '=roads__road_type', '=roads__suffix_direction')

    # Geo admin config
    point_zoom = 16
    modifiable = False    # TODO - doesn't hide "Delete all Features" link under map

admin.site.register(Road, RoadAdmin)
admin.site.register(RoadAlias)
admin.site.register(Intersection, IntersectionAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Landmark, admin.OSMGeoAdmin)
admin.site.register(LandmarkAlias)