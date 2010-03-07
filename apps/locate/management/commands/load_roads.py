import csv
import logging
log = logging.getLogger('safecity.locate.load_streets')
from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from apps.locate.models import *

DATA_DIR = 'data/streets'

class Command(NoArgsCommand):
    help = 'Import road locations into the database using the Django models. \
        Requires TIGER data in the database.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all road locations from the DB.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            logging.info("Clearing all road locations.")
            Block.objects.all().delete()
            Intersection.objects.all().delete()
            Road.objects.all().delete()
            
        for node in TigerNode.objects.all()[:100]:
            roads = []
            for block in node.tigerblock_set.all():
                tiger_road = block.road
                
                road, created = Road.objects.get_or_create(
                    name=tiger_road.name,
                    direction=tiger_road.direction,
                    suffix=tiger_road.suffix
                    )
                
                roads.append(road)
                
                # block_addr = str(block.from_addr_left)
                # block_name = Location.make_block_name(block_addr, road.direction, road.name)
                # 
                # block_loc, created = Location.objects.get_or_create(
                #     name=block_name,
                #     locale='BL',
                #     )
                
                # TODO - this effectively makes the exact location of a block random along
                # its length... it really should compute the center fron endpoints, but thats...
                # hard.
                # block_loc.location = node.location
                # block_loc.save()
                # 
                # block_loc.place_names.add(place)
        
            roads = set(roads)
            
            for oneway in roads:
                for otherway in roads:
                    # Never intersect with self
                    if oneway == otherway:
                        continue
                    
                    # Check if relationship already exists
                    exists = False
                    for i in oneway.intersections.all():
                        if otherway in i.roads.all():
                            exists = True
                            break
                            
                    if exists:
                        continue
                        
                    intersection = Intersection.objects.create(
                        location=node.location
                        )
                        
                    intersection.roads.add(oneway)    
                    intersection.roads.add(otherway)