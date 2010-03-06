import csv
import logging
log = logging.getLogger('safecity.locate.load_tiger')
from optparse import make_option
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
from django.core.management.base import NoArgsCommand, CommandError

from apps.locate.models import TigerRoad, TigerNode, TigerBlock

DATA_DIR = 'data/tiger'

class Command(NoArgsCommand):
    help = 'Import TIGER road data into the database using the Django models.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all TIGER data from the DB.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            logging.info("Clearing all TIGER data.")
            TigerBlock.objects.all().delete()
            TigerNode.objects.all().delete()
            TigerRoad.objects.all().delete()
        
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
            if not road_name or not road_dir or not road_type:
                continue
            
            road, created = TigerRoad.objects.get_or_create(
                name=road_name,
                suffix=road_type,
                direction=road_dir
                )
            
            nodes = []
            for pt in linestring.coords:
                try:
                    n = TigerNode.objects.filter(pt=Point(pt))[0]
                except IndexError:
                    n = TigerNode.objects.create(pt=Point(pt))
                nodes.append(n)
                
            block, created = TigerBlock.objects.get_or_create(
                road=road,
                from_addr_left=from_addr_left,
                to_addr_left=to_addr_left,
                from_addr_right=from_addr_right,
                to_addr_right=to_addr_right
                )
                
            for node in nodes:
                block.nodes.add(node)