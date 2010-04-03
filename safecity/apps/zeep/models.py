from django.contrib.gis import models

class JoinSession(models.Model):
    """
    Holding pen for users who have joined but not yet registered a location.
    """
    phone_number = models.CharField(
        primary_key=True,
        max_length=10,
        help_text='Phone number this resident joined with.')    

    datetime = models.DateTimeField(
        auto_now=True)

    def __unicode__(self):
        return self.phone_number
