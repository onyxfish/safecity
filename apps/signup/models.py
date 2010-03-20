from django.contrib.gis.db import models

class Resident(models.Model):
    """
    Individuals who want to receive alerts when activity happens near them.
    
    Privacy notes:
    1) The text used to register the resident is intentionally not associated with them.
    2) Created/updated times are not maintained so that any potentially sensitive information
        in their messages can never be associated with them.
    3) Residents are DELETED when a request is made to deregister them.
    """
    phone_number = models.CharField(
        primary_key=True,
        max_length=10,
        help_text='Phone number this resident registered with.')
    
    location = models.PointField(    
        spatial_index=True,
        help_text='Location extracted from request message. May not be null.')