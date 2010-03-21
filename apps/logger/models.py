import django
from django.db import models

class MessageBase(models.Model):
    """
    Base model for message logging.
    """
    text = models.CharField(
        max_length=160,
        help_text='Body of the message.')
    
    backend = models.CharField(
        max_length=150,
        help_text='System the message was received through.')
    
    class Meta:
        abstract = True
    
class IncomingMessage(MessageBase):
    """
    An incoming message before any processing.
    """
    sender = models.CharField(
        max_length=10,
        null=True,
        help_text='Phone number of sender. None if anonymized.')
        
    received = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time this message was received. Approximate if anonymized.')
    
    @property
    def identity(self):
        return self.sender
    
    @property
    def datetime(self):
        return self.received
    
    def is_incoming(self):
        return True
    
    def __unicode__(self):
        return "In from %s: %s" % (self.sender, self.text)

class OutgoingMessage(MessageBase):
    """
    An outgoing message from the system.
    """
    sent = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time that this message was sent. Approximate if anonymized.')
    
    @property
    def identity(self):
        return None
    
    @property
    def datetime(self):
        return self.sent
    
    def is_incoming(self):
        return False
    
    def __unicode__(self):
        return "Out: %s" % (self.text)