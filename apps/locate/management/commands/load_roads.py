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
            
        for node in TigerNode.objects.all():
            roads = []
            for tiger_block in node.tigerblock_set.all():
                tiger_road = tiger_block.road
                
                road, created = Road.objects.get_or_create(
                    name=tiger_road.name,
                    direction=tiger_road.direction,
                    suffix=tiger_road.suffix
                    )
                
                roads.append(road)
                
                addr = str(tiger_block.from_addr_left)
                
                # TODO - this effectively makes the exact location of a block random along
                # its length... it really should compute the center fron endpoints, but thats...
                # hard.
                block_num = Block.block_num_from_addr(addr)
                if not Block.objects.filter(number=block_num, road=road):
                    Block.objects.create(
                        number=block_num,
                        location=node.location,
                        road=road,
                        )
        
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