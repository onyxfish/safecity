from django.contrib.gis.db import models

ROAD_PREFIX_DIRECTIONS = {
    'N': 'NORTH',
    'S': 'SOUTH',
    'E': 'EAST',
    'W': 'WEST',
}

ROAD_TYPES = {
    'AVE': 'AVENUE',
    'BLVD': 'BOULEVARD',
    'CRES': 'CRESCENT',
    'CT': 'COURT',
    'DR': 'DRIVE',
    'ER': 'ENTRANCE RAMP',
    'EXPY': 'EXPRESSWAY',
    'LN': 'LANE',
    'HWY': 'HIGHWAY',
    'PKWY': 'PARKWAY',
    'PL': 'PLACE',
    'PLZ': 'PLAZA',
    'RL': 'RL (?)',       # Unknown abbrev. Only for "KENNEDY EXPRESS"
    'RD': 'ROAD',
    'ROW': 'ROW',
    'SQ': 'SQUARE',
    'SR': 'SR (?)',       # Unknown abbrev. e.g. "LAKE SHORE" and "KENNEDY EXPRESS"
    'ST': 'STREET',
    'TER': 'TERRACE',
    'TOLL': 'TOLLWAY',
    'WAY': 'WAY',
    'XR': 'EXIT RAMP',
}

ROAD_SUFFIX_DIRECTIONS = {
    'OP': 'OVERPASS',
    'S': 'SOUTH',
    'W': 'WEST',
    'EB': 'EASTBOUND',
    'WB': 'WESTBOUND',
    'N': 'NORTH',
    'OB': 'OUTBOUND',
    'NB': 'NORTHBOUND',
    'SB': 'SOUTHBOUND',
    'IB': 'INBOUND',
    'E': 'EAST',
}

ALIAS_TYPES = {
    'MS': 'Misspelling',
    'HN': 'Honorary Name',
}

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
        choices=ROAD_PREFIX_DIRECTIONS.items(),
        help_text='Direction this road runs.')
    
    name = models.CharField(
        max_length=64,
        db_index=True,
        help_text='The road name.')

    road_type = models.CharField(
        max_length=4,
        choices=ROAD_TYPES.items(),
        help_text='The road type, e.g. Ave.')

    suffix_direction = models.CharField(
        max_length=2,
        choices=ROAD_SUFFIX_DIRECTIONS.items(),
        help_text='Direction this road runs.')
        
    class Meta:
        ordering = ['name', 'road_type', 'prefix_direction', 'suffix_direction']
        
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
            bits.append(ROAD_PREFIX_DIRECTIONS[prefix_direction])
        
        bits.append(name)
        
        if road_type:
            bits.append(ROAD_TYPES[road_type])
            
        if suffix_direction:
            bits.append(ROAD_SUFFIX_DIRECTIONS[suffix_direction])
        
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

    alias_type = models.CharField(
        max_length=2,
        choices=ALIAS_TYPES.items(),
        help_text='The type of alias this is, e.g. Misspelling or Honorary Name')

class Intersection(models.Model):
    """
    A place where two or more Roads intersect.
    """
    roads = models.ManyToManyField(
        'Road',
        related_name='intersections')
    
    location = models.PointField()
    
    objects = models.GeoManager()
    
    def __unicode__(self):
        return ' and '.join([road.full_name for road in self.roads.all()])
    
    @classmethod
    def find_intersection(cls, oneway, otherway):
        """
        Lookup the intersection of two roads.
        """
        for i in oneway.intersections.all():
            if otherway in i.roads.all():
                return i

class Block(models.Model):
    """
    A single block of a road.
    """
    number = models.IntegerField(
        help_text='Start address number for this block, e.g. 1600.'
        )
        
    road = models.ForeignKey(
        'Road',
        help_text='The road this block is a part of.')
    
    location = models.PointField()
    
    objects = models.GeoManager()
    
    def __unicode__(self):
        return ' '.join([str(self.number), self.road.full_name])
    
    @classmethod
    def to_block_number(cls, x):
        return (x / 100) * 100

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