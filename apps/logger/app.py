import rapidsms

from apps.logger.models import OutgoingMessage, IncomingMessage

class App(rapidsms.app.App):
    
    def handle(self, message):
        """
        Log incoming messages.
        """
        msg = IncomingMessage.objects.create(
            sender=message.connection.identity,
            text=message.text,
            backend=message.connection.backend.slug)
            
        self.debug(msg)
    
    def outgoing(self, message):
        """
        Log outgoing messages
        """
        msg = OutgoingMessage.objects.create(
            text=message.text, 
            backend=message.connection.backend.slug)
                                             
        self.debug(msg)