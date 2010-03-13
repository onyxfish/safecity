import csv
import logging
log = logging.getLogger('safecity.locate.load_streets')
from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from apps.locate.models import *

DATA_DIR = 'data/streets'

class Command(NoArgsCommand):
    help = 'Extract locations from TIGER data.\
        Requires TIGER data in the database.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all locations from the DB.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            logging.info("Clearing all locations.")
            Block.objects.all().delete()
            Intersection.objects.all().delete()
            
        for node in TigerNode.objects.all():
            roads = []
            for tiger_segment in node.tigersegment_set.all():
                road = tiger_segment.road
                roads.append(road)
                
                blocks = self.extract_blocks_from_segment(tiger_segment)
                
                for block in blocks:
                    try:
                        Block.objects.get(
                            number=block[0],
                            road=road
                            )
                    except Block.DoesNotExist:
                        Block.objects.create(
                            number=block[0],
                            location=block[1],
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
        
    def extract_blocks_from_segment(self, segment):
        """
        Extract block information from a TIGER segement.
        
        Returns a list of tuples. Each tuple is of the form:
        (block_num, location).
        """
        if segment.from_addr_left < segment.from_addr_right:
            start = segment.from_addr_left
        else:
            start = segment.from_addr_right
            
        if segment.to_addr_left > segment.to_addr_right:
            end = segment.to_addr_left
        else:
            end = segment.to_addr_right
            
        # Awesome Python magic found here:
        # http://mail.python.org/pipermail/tutor/2003-August/024395.html    
        start = round(start, -2)
        end = round(end, -2)
        
        block_count = (end - start) / 100
        node_count = segment.nodes.count()
            
        blocks = [] 
        
        i = start
        while i <= end:
            # TODO: fix location hack
            node = TigerSegmentNode.objects.get(segment=segment, sequence=0).node
            blocks.append((str(int(i)), node.location))
            i += 100
        
        return blocks