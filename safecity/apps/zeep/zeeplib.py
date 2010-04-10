import base64
import hmac
import sha
import time

from django.conf import settings
from zeep.sms import connect

from safecity.lib.messages import *

ZEEP_CONNECTION = connect(settings.ZEEP_MOBILE_API_KEY, settings.ZEEP_MOBILE_SECRET_KEY)

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