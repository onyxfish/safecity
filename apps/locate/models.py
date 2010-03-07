from django.contrib.gis.db import models

LOCALES = (
    ('IN', 'Intersection'),
    ('BL', 'Block'),
    ('PK', 'Public Park'),
    ('LM', 'Landmark'),
)

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

class Location(models.Model):
    """
    Predefined locations in the city that can be used for quick geo-lookups.
    
    Note that a single physical location may have many entries in this table.
    """
    name = models.CharField(
        primary_key=True,
        max_length=100,
        help_text='A description of the location. E.g. "Austin & Augusta," "Millenium Park," or "1600 N Augusta."')
        
    location = models.PointField(
        help_text='Canonical location for this point.')
        
    locale = models.CharField(
        max_length=2,
        choices=LOCALES,
        help_text='The type of location that this point describes.')
        
    objects = models.GeoManager()
    
    @classmethod
    def make_intersection_name(cls, oneway, otherway):
        """
        Generate a standard name formate for a street intersection.
        """
        return '%s & %s' % (oneway, otherway)
        
    @classmethod
    def make_block_name(cls, addr, road_dir, road_name):
        """
        Generate a standard name format for a street block.
        """
        digits =  len(addr)
        if digits > 2:
            block_num = '%s00' % addr[:-2]
        else:
            block_num = '0'
            
        if road_dir:
            road_display = '%s. %s' % (road_dir, road_name)
        else:
            road_display = road_name
        
        return '%s block of %s' % (block_num, road_display)
        
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