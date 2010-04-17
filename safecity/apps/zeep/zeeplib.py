import logging
log = logging.getLogger("safecity.zeep.zeeplib")
import time

from django.conf import settings
from django.http import HttpResponse
from zeep.sms import Auth, connect

from safecity.lib.messages import *

ZEEP_CONNECTION = connect(settings.ZEEP_MOBILE_API_KEY, settings.ZEEP_MOBILE_SECRET_KEY)

# Helper functions

def zeep_timestamp():
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

# Exceptions

class ZeepUnexpectedEventException(Exception):
    pass

# Message subclasses
    
class ZeepIncomingMessage(IncomingMessage):
    """
    Back-end specific implementation of IncomingMessage.
    """
    def __init__(self, sender, text, received):
        super(ZeepIncomingMessage, self).__init__(
            sender, text, received, outgoing_cls=ZeepOutgoingMessage)
            
class ZeepOutgoingMessage(OutgoingMessage):
    """
    Back-end specific implementation of OutgoingMessage
    """ 
    def send(self):
        super(ZeepOutgoingMessage, self).send()
        
        for recipient in self.recipients:
            ZEEP_CONNECTION.send_message(recipient, self.text)
            
# Custom HttpResponse objects

class ZeepOkResponse(HttpResponse):
    def __init__(self):
        super(ZeepOkResponse, self).__init__(
            status=200,
            content_type='text/plain')
        
        self['Date'] = zeep_timestamp()
        self['Content-Length'] = 0

class ZeepReplyResponse(HttpResponse):
    def __init__(self, reply_text):
        super(ZeepReplyResponse, self).__init__(
            status=200,
            content_type='text/plain',
            content=reply_text)
            
        self['Date'] = zeep_timestamp()
        self['Content-Length'] = len(reply_text)