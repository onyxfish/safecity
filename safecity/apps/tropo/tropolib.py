import logging
log = logging.getLogger("safecity.tropo.tropolib")
import time
from urllib import urlencode
from urllib2 import urlopen

from django.conf import settings
from django.http import HttpResponse

from safecity.lib.messages import *

TROPO_URL = 'http://api.tropo.com/1.0/sessions'
TROPO_TOKEN = '610c578baff94548b4c19d3389494bea03905dc92b60f6d84c7aa9e26fa10688b242f1f151a0cf1f1d993ad2'

# Exceptions

# Message subclasses
    
class TropoIncomingMessage(IncomingMessage):
    """
    Back-end specific implementation of IncomingMessage.
    """
    def __init__(self, sender, text, received):
        super(TropoIncomingMessage, self).__init__(
            sender, text, received, outgoing_cls=TropoOutgoingMessage)
            
class TropoOutgoingMessage(OutgoingMessage):
    """
    Back-end specific implementation of OutgoingMessage
    """ 
    def send(self):
        super(TropoOutgoingMessage, self).send()
        
        params = {
            'action': 'create',
            'token': TROPO_TOKEN,
            'recipients': ','.join(self.recipients),
            'text': self.text,
        }
        
        url = '?'.join([TROPO_URL, urlencode(params)])
        
        urlopen(url)
            
# Custom HttpResponse objects

class TropoOkResponse(HttpResponse):
    def __init__(self):
        super(TropoOkResponse, self).__init__(status=200)