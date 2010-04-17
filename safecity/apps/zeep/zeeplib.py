import logging
log = logging.getLogger("safecity.zeep.zeeplib")

from django.conf import settings
from django.http import HttpResponse
from zeep.sms import Auth, connect

from safecity.lib.messages import *

ZEEP_CONNECTION = connect(settings.ZEEP_MOBILE_API_KEY, settings.ZEEP_MOBILE_SECRET_KEY)

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

class ZeepReplyResponse(HttpResponse):
    def __init__(self, reply_text):
        super(ZeepReplyResponse, self).__init__(
            status=200,
            content_type='text/plain',
            content=reply_text)
    #         
    #     self._sign()
    #         
    # def _sign(self):
    #     signature = Auth.calculate_signature(
    #         self.content,
    #         settings.ZEEP_MOBILE_API_KEY,
    #         settings.ZEEP_MOBILE_SECRET_KEY)
    #         
    #     self['Authorization'] = 'Zeep %s:%s' % (settings.ZEEP_MOBILE_API_KEY, signature)