from django.contrib.gis.db import models

class Citizen(models.Model):
    """
    Individuals who want to receive alerts when activity happens near them.
    """
    on_text = models.CharField(
        max_length=160,
        help_text='Body of the message that enabled broadcasts for this user.')
    
    location = models.PointField(    
        spatial_index=True,
        help_text='Location extracted from request message. May not be null.')