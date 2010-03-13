from django.contrib.gis.db import models

TIGER_ROAD_TYPES = (
    ('Ave', 'Avenue'),
    ('Blvd', 'Boulevard'),
    ('Cir', 'Circle'),
    ('Ct', 'Court'),
    ('Dr', 'Drive'),
    ('Ln', 'Lane'),
    ('Pky', 'Parkway'),
    ('Pl', 'Place'),
    ('Rd', 'Road'),
    ('St', 'Street'),
    ('Ter', 'Terrace'),
    ('Trl', 'Trl'),         # ???
    ('Walk', 'Walk'),       # ???
    ('Way', 'Way'),
    ('Xing', 'Crossing')
)

TIGER_ROAD_DIRS = (
    ('N', 'North'),
    ('NE', 'Northeast'),
    ('E', 'East'),
    ('SE', 'Southeast'),
    ('S', 'South'),
    ('SW', 'Southwest'),
    ('W', 'West'),
    ('NW', 'Northwest'),
)

class Road(models.Model):
    """
    A unique named street in the city.
    """
    full_name = models.CharField(
        primary_key=True,
        max_length=100,
        help_text='A summarization of direction, name, and suffix.'
    )
    
    direction = models.CharField(
        max_length=2,
        choices=TIGER_ROAD_DIRS,
        help_text='Direction this road runs.')
    
    name = models.CharField(
        max_length=64,
        help_text='The road name.')

    suffix = models.CharField(
        max_length=4,
        help_text='The road type, e.g. Ave.')
        
    def __unicode__(self):
        return self.full_name
        
    def save(self, *args, **kwargs):
        """
        Populate the full_name property before saving.
        """
        if not self.full_name:
            self.full_name = Road.make_full_name(self.direction, self.name, self.suffix)
        
        return super(Road, self).save(*args, **kwargs)
        
    @classmethod
    def make_full_name(cls, direction, name, suffix):
        if direction:
            dir_and_name = '%s %s' % (direction, name)
        else:
            dir_and_name = name
        
        return '%s %s' % (dir_and_name, suffix)
        
class RoadAlias(models.Model):
    """
    An alternate name for a Road.
    """
    name = models.CharField(
        primary_key=True,
        max_length=64,
        help_text='Alternate name or spelling for a Road.')
        
    road = models.ForeignKey('Road')

class Intersection(models.Model):
    """
    A place where two Roads intersect.
    """
    roads = models.ManyToManyField('Road', related_name='intersections')
    
    location = models.PointField()
    
    objects = models.GeoManager()

class Block(models.Model):
    """
    A single block of a road.
    """
    number = models.CharField(
        max_length=5,
        help_text='Start address number for this block, e.g. 1600.'
        )
        
    road = models.ForeignKey('Road')
    
    location = models.PointField()
    
    objects = models.GeoManager()
    
    @classmethod
    def block_num_from_addr(cls, addr):
        digits = len(addr)
        if digits > 2:
            return '%s00' % addr[:-2]
        else:
            return '0'

class Landmark(models.Model):
    """
    A location that is unique but not defined by streets, such as
    a park, plaza, or building name.
    """
    name = models.CharField(
        primary_key=True,
        max_length=64,
        help_text='Name of the landmark.')

    location = models.PointField()
    
    objects = models.GeoManager()
    
class LandmarkAlias(models.Model):
    """
    An alternate name or spelling for a Landmark.
    """
    name = models.CharField(
        primary_key=True,
        max_length=64,
        help_text='Alternate name or spelling for a Landmark.')
        
    road = models.ForeignKey('Road')
        
# Intermediate models for loading TIGER data

class TigerNode(models.Model):
    """
    Imported node/point information from census TIGER data.
    """
    location = models.PointField()

    objects = models.GeoManager()

class TigerSegment(models.Model):
    """
    Imported segment informtaion from census TIGER data.
    
    Note: A segment may contain multiple blocks.
    """
    road = models.ForeignKey('Road')
    
    linestring = models.LineStringField(
        help_text='The original linestring for this segment.'
        )
    
    nodes = models.ManyToManyField('TigerNode',
        through='TigerSegmentNode',
        help_text='Two or more points that define this block.')
    
    from_addr_left = models.IntegerField()
    to_addr_left = models.IntegerField()
    from_addr_right = models.IntegerField()
    to_addr_right = models.IntegerField()
    
class TigerSegmentNode(models.Model):
    """
    Intermediate table for ManyToMany relationship between
    TigerNode and TigerSegment that adds a sequence column.
    """
    node = models.ForeignKey('TigerNode')
    segment = models.ForeignKey('TigerSegment')
    sequence = models.IntegerField()
    
    