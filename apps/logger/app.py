import rapidsms

from apps.logger.models import OutgoingMessage, IncomingMessage
from apps.priorities import PRIORITIES

class App(rapidsms.app.App):
    """
    Handles logging of all inbound and outbound traffic.
    
    This data is purely for analytics--processed data is logged elsewhere.
    (e.g in the danger app)
    """
    PRIORITY = PRIORITIES['logger']
    
    def handle(self, message):
        """
        Log incoming messages.  Annotate log entry onto message object.
        """
        message.log_entry = IncomingMessage.objects.create(
            sender=message.connection.identity,
            text=message.text,
            backend=message.connection.backend.slug)
            
        self.debug(message.log_entry)
    
    def outgoing(self, message):
        """
        Log outgoing messages
        """
        message.log_entry = OutgoingMessage.objects.create(
            text=message.text, 
            backend=message.connection.backend.slug)
                                             
        self.debug(message.log_entry)