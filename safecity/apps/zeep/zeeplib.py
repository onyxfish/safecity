import base64
import hmac
import sha
import time

from django.conf import settings
from zeep.sms import connect

from safecity.lib.messages import *

ZEEP_CONNECTION = connect(settings.ZEEP_API_KEY, settings.ZEEP_SECRET_KEY)

class ZeepIncomingMessage(IncomingMessage):
    """
    Back-end specific implementation of IncomingMessage.
    """
    def __init__(sender, text, received):
        super(self, IncomingMessage).__init__(
            sender, text, received, outgoing_cls=ZeepOutgoingMessage)
            
class ZeepOutgoingMessage(OutgoingMessage):
    """
    Back-end specific implementation of OutgoingMessage
    """ 
    def send():
        super(self, OutgoingMessage).send()
        
        for recipient in self.recipients:
            ZEEP_CONNECTION.send_message(recipient, self.text)