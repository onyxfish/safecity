from django.contrib.gis.db import models

class Road(models.Model):
    """
    A unique named street in the city.
    """
    full_name = models.CharField(
        primary_key=True,
        max_length=100,
        help_text='A cat\'d version of prefix_direction, name, road_type, and suffix_direction.'
    )
    
    prefix_direction = models.CharField(
        max_length=2,
        help_text='Direction this road runs.')
    
    name = models.CharField(
        max_length=64,
        help_text='The road name.')

    road_type = models.CharField(
        max_length=4,
        help_text='The road type, e.g. Ave.')

    suffix_direction = models.CharField(
        max_length=2,
        help_text='Direction this road runs.')
        
    def __unicode__(self):
        return self.full_name
        
    def save(self, *args, **kwargs):
        """
        Populate the full_name property before saving.
        """
        if not self.full_name:
            self.full_name = Road.make_full_name(
                self.prefix_direction, self.name, self.road_type, self.suffix_direction)
        
        return super(Road, self).save(*args, **kwargs)
        
    @classmethod
    def make_full_name(cls, prefix_direction, name, road_type, suffix_direction):
        """
        Generate a unique road ID based on name parts.
        """
        bits = []
        
        if prefix_direction:
            bits.append(prefix_direction)
        
        bits.append(name)
        
        if road_type:
            bits.append(road_type)
            
        if suffix_direction:
            bits.append(suffix_direction)
        
        return ' '.join(bits)
        
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
    number = models.IntegerField(
        help_text='Start address number for this block, e.g. 1600.'
        )
        
    road = models.ForeignKey('Road')
    
    location = models.PointField()
    
    objects = models.GeoManager()
    
    def __unicode__(self):
        return ' '.join([str(self.number), self.road])

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

# TIGER_ROAD_TYPES = (
#     ('Ave', 'Avenue'),
#     ('Blvd', 'Boulevard'),
#     ('Cir', 'Circle'),
#     ('Ct', 'Court'),
#     ('Dr', 'Drive'),
#     ('Ln', 'Lane'),
#     ('Pky', 'Parkway'),
#     ('Pl', 'Place'),
#     ('Rd', 'Road'),
#     ('St', 'Street'),
#     ('Ter', 'Terrace'),
#     ('Trl', 'Trl'),         # ???
#     ('Walk', 'Walk'),       # ???
#     ('Way', 'Way'),
#     ('Xing', 'Crossing')
# )
# 
# TIGER_ROAD_DIRS = (
#     ('N', 'North'),
#     ('NE', 'Northeast'),
#     ('E', 'East'),
#     ('SE', 'Southeast'),
#     ('S', 'South'),
#     ('SW', 'Southwest'),
#     ('W', 'West'),
#     ('NW', 'Northwest'),
# )

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
    
# Intermediate tables for loading centerline data

# class 