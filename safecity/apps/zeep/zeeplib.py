from safecity.lib.messages import *

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
        
        # TODO