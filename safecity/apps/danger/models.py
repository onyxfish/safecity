from django.contrib.gis.db import models
from django.contrib.gis.measure import D

from safecity.apps.signup.models import Resident

class Report(models.Model):
    """
    Processed data for messages that are reporting suspicious activity.
    
    TODO: support multi-part messages.
    """
    location = models.PointField(
        spatial_index=True,
        help_text='Location extracted from the report.')
        
    text = models.CharField(
        max_length=160,
        help_text='Body of the message.')
        
    sender = models.CharField(
        max_length=16,
        null=True,
        help_text='Phone number of the reporter in e164 format. None if anonymized.')
        
    received = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time this message was received. Approximate if anonymized.')

    objects = models.GeoManager()
    
    class Meta:
        ordering = ['-received']
        get_latest_by = 'received'
        
    def find_nearby_residents(self):
        """
        Get a list of residents near this report.
        """
        return Resident.objects.filter(location__distance_lte=(self.location, D(km=1)))