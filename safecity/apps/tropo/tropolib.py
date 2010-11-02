import logging
log = logging.getLogger("safecity.tropo.tropolib")
import time
from urllib import urlencode
from urllib2 import urlopen

from django.conf import settings
from django.http import HttpResponse

from safecity.lib.messages import *

TROPO_URL = 'http://api.tropo.com/1.0/sessions'

# Exceptions

# Message subclasses
    
class TropoIncomingMessage(IncomingMessage):
    """
    Back-end specific implementation of IncomingMessage.
    """
    def __init__(self, sender, text, received):
        super(TropoIncomingMessage, self).__init__(
            sender, text, received, outgoing_cls=TropoOutgoingMessage)

        if settings.DEBUG: 
            log.debug('Created TropoIncomingMessage: %s, %s' % (sender, text)) 
            
class TropoOutgoingMessage(OutgoingMessage):
    """
    Back-end specific implementation of OutgoingMessage
    """ 
    def send(self):
        super(TropoOutgoingMessage, self).send()
        
        params = {
            'action': 'create',
            'token': settings.TROPO_TOKEN,
            'recipients': ','.join(self.recipients),
            'text': self.text,
        }
        
        url = '?'.join([TROPO_URL, urlencode(params)])
        
        if settings.DEBUG:
            log.debug('Sending TropoOutgoingMessage: %s' % url)
            
        urlopen(url)
            
# Custom HttpResponse objects

class TropoOkResponse(HttpResponse):
    def __init__(self):
        super(TropoOkResponse, self).__init__(status=200)
