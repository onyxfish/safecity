import csv
import logging
log = logging.getLogger('safecity.locate.load_streets')
from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from apps.locate.models import *

DATA_DIR = 'data/streets'

class Command(NoArgsCommand):
    help = 'Import street locations into the database using the Django models.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all street locations from the DB.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            logging.info("Clearing all street locations.")
            Location.objects.filter(locale__in=['IN', 'BL']).delete()
            
        for node in TigerNode.objects.all()[:100]:
            roads = []
            for block in node.tigerblock_set.all():
                road = block.road
                roads.append(road.name)
                
                block_addr = str(block.from_addr_left)
                block_name = Location.make_block_name(block_addr, road.direction, road.name)
                
                block_loc, created = Location.objects.get_or_create(
                    name=block_name,
                    # location=,
                    locale='BL',
                    )
        
            roads = list(set(roads))
            
            for oneway in roads:
                for otherway in roads:
                    if oneway == otherway:
                        continue
                        
                    intersection_name = Location.make_intersection_name(oneway, otherway)
                    
                    intersection, created = Location.objects.get_or_create(
                        name=intersection_name,
                        # location=,
                        locale='IN',
                        )