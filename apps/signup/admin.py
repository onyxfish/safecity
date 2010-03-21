from django.contrib.gis import admin

from apps.signup.models import Resident

admin.site.register(Resident, admin.OSMGeoAdmin)