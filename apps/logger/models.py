import django
from django.db import models

class MessageBase(models.Model):
    """
    Base model for message logging.
    """
    text = models.CharField(max_length=160)
    backend = models.CharField(max_length=150)
    
    class Meta:
        abstract = True
    
class IncomingMessage(MessageBase):
    """
    An incoming message before any processing.
    """
    sender = models.CharField(max_length=10)
    received = models.DateTimeField(auto_now_add=True)
    
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
    sent = models.DateTimeField(auto_now_add=True)
    
    @property
    def identity(self):
        return 'Anonymous'
    
    @property
    def datetime(self):
        return self.sent
    
    def is_incoming(self):
        return False
    
    def __unicode__(self):
        return "Out to %s: %s" % (self.recipient, self.text)