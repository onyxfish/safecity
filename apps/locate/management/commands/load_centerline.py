import csv
from optparse import make_option
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal.error import OGRException
from django.contrib.gis.geos import fromstr, Point
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection, transaction

from rapidsms.log import Logger
log = Logger(level='Debug')

from apps.locate.models import *

DATA_DIR = 'data/centerline'

class Command(NoArgsCommand):
    title = 'locate.load_centerline'
    help = 'Import centerline road data into the database using the Django models.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all centerline data from the DB.'),
        make_option('-t', '--test', action='store_true', dest='test',
            help='Load test centerline data.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            log.write(self, 'INFO', 'Clearing all centerline data.')
            Intersection.objects.all().delete()
            Block.objects.all().delete()
            Road.objects.all().delete()
            
        log.write(self, 'INFO', 'Reading shapefile.')
        
        if options['test']:
            shapefile = os.path.join(DATA_DIR, 'test/test.shp')
        else:
            shapefile = os.path.join(DATA_DIR, 'full/Transportation.shp')
            
        ds = DataSource(shapefile)
        layer = ds[0]
        
        log.write(self, 'INFO', 'Importing features.')
        
        for feature in layer:
            road_name = feature.get('STREET_NAM')
            road_prefix_direction = feature.get('PRE_DIR')
            road_type = feature.get('STREET_TYP')
            road_suffix_direction = feature.get('SUF_DIR')
            from_cross_road = feature.get('F_CROSS')
            to_cross_road = feature.get('T_CROSS')
            
            try:
                linestring = feature.geom
            except OGRException:
                continue
            
            # The vast majority of these unnammed roads are at O'Hare.
            # If they don't have names then people can't refer to them anyway
            # So we just skip them.
            if not road_name:
                continue
            
            # Create road for this feature
            road = self.get_or_create_road(
                road_prefix_direction, road_name, road_type, road_suffix_direction)
            
            # Create a block for this feature
            self.create_block_for_feature(feature, road)
        
            # Create roads from intersecting features
            if from_cross_road:
                f_road = self.get_road_for_intersection(from_cross_road)
                
                if f_road:
                    location = Point(linestring.coords[0], srid=9102671)
                    self.create_intersection(road, f_road, location)
            
            if to_cross_road:
                t_road = self.get_road_for_intersection(to_cross_road)
                
                if t_road:
                    location = Point(linestring.coords[-1], srid=9102671)
                    self.create_intersection(road, t_road, location)
                    
        log.write(self, 'INFO', 'Finished.')
        
    def get_or_create_road(self, road_prefix_direction, road_name, road_type, road_suffix_direction):
        """
        Condense boiler-plate for retrieving and creating roads.
        """
        full_name = Road.make_full_name(
            road_prefix_direction, road_name, road_type, road_suffix_direction)
        try:
            road = Road.objects.get(full_name=full_name)
        except Road.DoesNotExist:
            road = Road.objects.create(
                full_name=full_name,
                prefix_direction=road_prefix_direction,
                name=road_name,
                road_type=road_type,
                suffix_direction=road_suffix_direction
                )
                
        return road
        
    def get_road_for_intersection(self, cross):
        """
        Creates a road from the centerline F_CROSS or T_CROSS strings,
        if those strings indicate an intersection w/ another road.
        """
        bits = cross.split('|')[1:] # Trim address number
        bits = [bit.strip() for bit in bits] # Cleanup whitespace
        
        road_name = bits[1].strip()
        if road_name and road_name != 'DEAD END':
            road = self.get_or_create_road(*bits)
        else:
            # Road connects to another block of the same road w/o intersection
            # or the Road just ends
            road = None
            
        return road
        
    def create_block_for_feature(self, feature, road):  
        """
        Creates a block from a given feature.
        """     
        from_addr_left = feature.get('L_F_ADD')
        to_addr_left = feature.get('L_T_ADD')
        from_addr_right = feature.get('R_F_ADD')
        to_addr_right = feature.get('R_T_ADD')
        
        try:
            linestring = feature.geom
        except OGRException:
            return
        
        block_number = self.get_block_number(
            from_addr_left, to_addr_left, from_addr_right, to_addr_right)
            
        # Get center-point of block
        location = fromstr(self.estimate_point_along_linestring(linestring, 0.50), srid=9102671)
        
        try:
            Block.objects.get(
                number=block_number,
                road=road
                )
        except Block.DoesNotExist:
            Block.objects.create(
                number=block_number,
                road=road,
                location=location
                )
                
    def get_block_number(self, from_addr_left, to_addr_left, from_addr_right, to_addr_right):
        """
        Gets the number of a block from its address range.
        """
        if from_addr_left < from_addr_right:
            from_addr = from_addr_left
        else:
            from_addr = from_addr_right

        if to_addr_left > to_addr_right:
            to_addr = to_addr_left
        else:
            to_addr = to_addr_right

        if to_addr < from_addr:
            raise Exception('Unexpected data: to_addr < from_addr')

        return Block.to_block_number(from_addr)
        
    def estimate_point_along_linestring(self, linestring, percent):
        """
        Use PostGIS's ST_Line_Interpolate_Point function to estimate
        a point along a linestring.
        """
        cursor = connection.cursor()

        linestring = linestring.wkt

        cursor.execute("\
            SELECT ST_AsText(ST_Line_Interpolate_Point(the_line, %f))\
        	    FROM (SELECT ST_GeomFromEWKT('%s') as the_line) As foo;" % (percent, linestring))
        row = cursor.fetchone()

        return row[0]
        
    def create_intersection(self, oneway, otherway, location):
        """
        Create an intersection for two Roads.
        """
        try:
            intersection = Intersection.objects.get(location=location)
        except Intersection.DoesNotExist:
            intersection = Intersection.objects.create(
                location=location
                )
        
        intersection_roads = intersection.roads.all()
        
        if oneway not in intersection_roads:
            intersection.roads.add(oneway)
        
        if otherway not in intersection_roads:    
            intersection.roads.add(otherway)