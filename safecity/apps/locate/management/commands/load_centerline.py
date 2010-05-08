import csv
import logging
log = logging.getLogger("safecity.locate.load_centerline")
from optparse import make_option
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal.error import OGRException
from django.contrib.gis.geos import fromstr, LineString, MultiLineString, Point
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection, transaction

from safecity.apps.locate.models import *

DATA_DIR = 'data/centerline'

class NoAddressesException(Exception):
    """
    Exception raise when a block has no zoned addresses.
    """
    pass
    
class InvalidAddressRangeException(Exception):
    """
    Raised when a block's address data does not match expectations.
    """
    pass

class Command(NoArgsCommand):
    title = 'locate.load_centerline'
    help = 'Import centerline road data into the database using the Django models.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all centerline data from the DB.'),
        make_option('-t', '--test', action='store_true', dest='test',
            help='Load test centerline data.'),
        make_option('-d', '--demo', action='store_true', dest='demo',
            help='Load demo centerline data.'),
        )
        
    paths = {}

    def handle_noargs(self, **options):
        if options['clear']:
            log.info('Clearing all centerline data.')
            Intersection.objects.all().delete()
            Block.objects.all().delete()
            Road.objects.all().delete()
            
        log.info('Reading shapefile.')
        
        if options['test']:
            shapefile = os.path.join(DATA_DIR, 'test/test.shp')
        elif options['demo']:
            shapefile = os.path.join(DATA_DIR, 'loop/loop.shp')
        else:
            shapefile = os.path.join(DATA_DIR, 'full/Transportation.shp')
            
        ds = DataSource(shapefile)
        layer = ds[0]
        
        log.info('Importing features.')
        
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
        
        for k, v in self.paths.items():
            # Remaing lines that can't be merged have a fork, divided road, or other anomaly
            if len(v) > 1 and type(v.merged) == MultiLineString:
                log.warn('Unable to merge block segments: %s %s' % k)
                    
        log.info('Finished.')
        
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
        
        try:
            block_number = self.get_block_number(
                from_addr_left, to_addr_left, from_addr_right, to_addr_right)
        except NoAddressesException:
            # For our purposes a block without addresses is no block at all
            log.debug('Skipping block creation for segment of %s with no addresses.' % road.full_name)
            return
        except InvalidAddressRangeException:
            # Don't die on these types of errors--will fix them as we can
            log.error('Invalid address range for segment of %s, bounds were %s, %s, %s, %s.' % 
                (road.full_name, from_addr_left, to_addr_left, from_addr_right, to_addr_right))
            return
            
        try:
            block = Block.objects.get(
                number=block_number,
                road=road
                )
                
            # Add new segment to set composing this block
            self.paths[(block_number, road)].append(linestring.geos)
            
            # Attempt to merge line set
            path = self.paths[(block_number, road)].merged
            
            # If the merge succeeded this will be LineString (otherwise MultiLineString)
            if type(path) == LineString:
                location = fromstr(self.estimate_point_along_linestring(path, 0.50), srid=9102671)
                block.location = location
                block.save()
            else:
                # Discontinous segments could not be merged, assume there are more to come.
                return
        except Block.DoesNotExist:
            # Get center-point of segment
            location = fromstr(self.estimate_point_along_linestring(linestring, 0.50), srid=9102671)
                
            Block.objects.create(
                number=block_number,
                road=road,
                location=location
                )
                
            # Store linestring in case this block turns out to have multiple segments
            self.paths[(block_number, road)] = MultiLineString(linestring.geos)
                
    def get_block_number(self, from_addr_left, to_addr_left, from_addr_right, to_addr_right):
        """
        Gets the number of a block from its address range.
        """
        # No addresses on left side of road
        if from_addr_left == 0 and to_addr_left == 0:
            # No addresses on either side
            if from_addr_right == 0 and to_addr_right == 0:
                raise NoAddressesException()
            
            from_addr = from_addr_right
            to_addr = to_addr_right
        # No addresses on right side
        elif from_addr_right == 0 and to_addr_right == 0:
            from_addr = from_addr_left
            to_addr = to_addr_left
        # Address on both sides
        else:
            if from_addr_left < from_addr_right:
                from_addr = from_addr_left
            else:
                from_addr = from_addr_right

            if to_addr_left > to_addr_right:
                to_addr = to_addr_left
            else:
                to_addr = to_addr_right

        if to_addr < from_addr:
            raise InvalidAddressRangeException()

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