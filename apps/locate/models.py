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
    
    name = models.CharField(
        max_length=64,
        help_text='The road name.')

    suffix = models.CharField(
        max_length=4,
        help_text='The road type, e.g. Ave.')
    
    direction = models.CharField(
        max_length=2,
        choices=TIGER_ROAD_DIRS,
        help_text='Direction this road runs.')
        
    def __unicode__(self):
        return self.full_name
        
    def save(self, *args, **kwargs):
        """
        Populate the full_name property before saving.
        """
        if self.direction:
            dir_and_name = '%s %s' % (self.direction, self.name)
        else:
            dir_and_name = self.name
            
        self.full_name = '%s %s' % (dir_and_name, self.suffix)
        
        return super(Road, self).save(*args, **kwargs)
        
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
        
# Supplemental models for loading TIGER data

class TigerRoad(models.Model):
    """
    Imported road information from census TIGER data.
    """
    name = models.CharField(
        max_length=100,
        help_text='The road name.')
    
    suffix = models.CharField(
        max_length=4,
        help_text='The road type, e.g. Ave.')
        
    direction = models.CharField(
        max_length=2,
        choices=TIGER_ROAD_DIRS,
        help_text='Direction this road runs.')
    
    class Meta:
        unique_together = (('name', 'suffix', 'direction'),)

class TigerNode(models.Model):
    """
    Imported node/point information from census TIGER data.
    """
    location = models.PointField()

    objects = models.GeoManager()

class TigerBlock(models.Model):
    """
    Imported block informtaion from census TIGER data.
    
    TODO: is this really a "block"? or just a segment.
    """
    road = models.ForeignKey('TigerRoad')
    
    nodes = models.ManyToManyField('TigerNode',
        help_text='Two or more points that define this block.')
    
    from_addr_left = models.IntegerField()
    to_addr_left = models.IntegerField()
    from_addr_right = models.IntegerField()
    to_addr_right = models.IntegerField()