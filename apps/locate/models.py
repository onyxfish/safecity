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
    display_name = models.CharField(
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
        
    def save(self, *args, **kwargs):
        if self.direction:
            dir_and_name = '%s %s' % (self.direction, self.name)
        else:
            dir_and_name = self.name
            
        self.display_name = '%s %s' % (dir_and_name, self.suffix)
        
        return super(Road, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('name', 'suffix', 'direction'),)

class Intersection(models.Model):
    """
    A place where two Roads intersect.
    """
    # TODO: implement MAX of 2 for this join?
    roads = models.ManyToManyField('Road', related_name='intersections')
    
    location = models.PointField()
    
    objects = models.GeoManager()
    
class Block(models.Model):
    """
    TODO
    """
    objects = models.GeoManager()

class Landmark(models.Model):
    """
    TODO
    """    
    objects = models.GeoManager()
        
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