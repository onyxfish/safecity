from django.contrib.gis.db import models

LOCALES = (
    ('CR', 'Street Corner/Intersection'),
    ('ST', 'Street Block'),
    ('PK', 'Public Park'),
    ('LM', 'Landmark'),
)

class Location(models.Model):
    """
    Predefined locations in the city that can be used for quick geo-lookups.
    """
    name = models.CharField(
        max_length=100,
        help_text='A description of the location. E.g. "Austin & Augusta," "Millenium Park," or "1600 N Augusta."')
        
    location = models.PointField(
        null=True,
        help_text='Canonical location for this point.')
        
    locale = models.CharField(
        max_length=2,
        choices=LOCALES,
        help_text='The type of location that this point describes.')