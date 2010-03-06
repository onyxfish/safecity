from django.contrib.gis.db import models

class Report(models.Model):
    """
    Message data for messages that are reporting suspicious activity.
    
    TODO: support multi-part messages.
    """
    text = models.CharField(
        max_length=160,
        help_text='Body of the received message.')
        
    timestamp = models.DateTimeField(
        db_index=True,
        help_text='The date and time that this message was received.')
        
    location = models.PointField(
        null=True,
        help_text='Location extracted from text. May be null if a location could not be deteremined.')
        
    reporter = models.CharField(
        max_length=10,
        null=True,
        help_text='The phone number of the reporter. Will be null once the message has been anonymized.')
        
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