import csv
import logging
log = logging.getLogger('safecity.locate.load_streets')
from optparse import make_option

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection, transaction

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
                            location=GEOSGeometry(block[1]),
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
        
        if start > end:
            start, end = end, start
            backwards_street = True
        else:
            backwards_street = False
        
        start = floor_to_hundreds(start)
        end = floor_to_hundreds(end)
        
        block_count = ((end - start) / 100) + 1
        fraction = 1.0 / block_count    # Divide the line into equal segments
            
        blocks = []
                
        i = 0
        for i in range(0, block_count):
            # Find the point halfway along this fraction's portion of the line
            percent = (fraction * i) + fraction * 0.5
            
            # For streets running the opposite direction, invert the fraction
            if backwards_street:
                percent = 1.0 - percent
                            
            location = self.estimate_point_along_segment(segment, percent)
            blocks.append((str(int(start + i * 100)), location))
        
        return blocks
        
    def estimate_point_along_segment(self, segment, percent):
        """
        Use PostGIS's ST_Line_Interpolate_Point function to estimate
        a point along a linestring.
        """
        cursor = connection.cursor()
        
        linestring = segment.linestring.wkt

        cursor.execute("\
            SELECT ST_AsText(ST_Line_Interpolate_Point(the_line, %f))\
        	    FROM (SELECT ST_GeomFromEWKT('%s') as the_line) As foo;" % (percent, linestring))
        row = cursor.fetchone()

        return row[0]
        
def floor_to_hundreds(x):
     return (x / 100) * 100