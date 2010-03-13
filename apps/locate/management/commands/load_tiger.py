import csv
from rapidsms import log as rlog
log = rlog.Logger(level='Debug')
from optparse import make_option
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
from django.core.management.base import NoArgsCommand, CommandError
from django.db import IntegrityError

from apps.locate.models import *

DATA_DIR = 'data/tiger'

class Command(NoArgsCommand):
    help = 'Import TIGER road data into the database using the Django models.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all TIGER data from the DB.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            log.write('', 'info', 'Clearing all TIGER data.')
            TigerSegment.objects.all().delete()
            TigerNode.objects.all().delete()
            Road.objects.all().delete()
        
        shapefile = os.path.join(DATA_DIR, 'cookcounty/tgr17031lkA.shp')
            
        ds = DataSource(shapefile)
        layer = ds[0]
        
        for feature in layer:
            road_name = feature.get('FENAME')
            road_dir = feature.get('FEDIRP')
            road_type = feature.get('FETYPE')
            from_addr_left = feature.get('FRADDL')
            to_addr_left = feature.get('TOADDL')
            from_addr_right = feature.get('FRADDR')
            to_addr_right = feature.get('TOADDR')
            linestring = feature.geom
            
            # TODO: bad data?
            if not road_name:
                continue
                
            full_name = Road.make_full_name(road_dir, road_name, road_type)
            try:
                road = Road.objects.get(full_name=full_name)
            except Road.DoesNotExist:
                road = Road.objects.create(
                    full_name=full_name,
                    direction=road_dir,
                    name=road_name,
                    suffix=road_type
                    )
            
            nodes = []
            for pt in linestring.coords:
                point = Point(pt)
                try:
                    n = TigerNode.objects.filter(location__equals=point)[0]
                except IndexError:
                    n = TigerNode.objects.create(location=point)
                nodes.append(n)
            
            segment = TigerSegment.objects.create(
                road=road,
                linestring=linestring.geos,
                from_addr_left=from_addr_left,
                to_addr_left=to_addr_left,
                from_addr_right=from_addr_right,
                to_addr_right=to_addr_right
                )
            
            i = 0
            for node in nodes:
                TigerSegmentNode.objects.create(
                    node=node,
                    segment=segment,
                    sequence=i
                )
                i += 1