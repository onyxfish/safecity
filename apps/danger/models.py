from django.contrib.gis.db import models
from django.contrib.gis.measure import D

from apps.signup.models import Resident

class Report(models.Model):
    """
    Processed data for messages that are reporting suspicious activity.
    
    Note that message-text, phone number, and timestamp and not reproduced
    from the log entry so that they can be centrally anonymized.
    
    TODO: support multi-part messages.
    """
    location = models.PointField(
        spatial_index=True,
        help_text='Location extracted from the report.')
        
    log_entry = models.ForeignKey(
        'logger.IncomingMessage',
        
        help_text='The log entry for this report.')

    objects = models.GeoManager()
        
    def find_nearby_residents(self):
        """
        Get a list of residents near this report.
        """
        return Resident.objects.filter(location__distance_lte=(self.location, D(km=1)))