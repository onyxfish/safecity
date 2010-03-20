import rapidsms

from apps.priorities import PRIORITIES

class App(rapidsms.app.App):
    """
    This application handles receiving, parsing, and broadcasting reports of
    suspicious behavior (gang activity, etc).
    
    Depends on the "locate" app.
    """
    PRIORITY = PRIORITIES['danger']
    
    def handle (self, message):
        """
        Store the message and rebroadcast it to appropriate recipients.
        
        TODO
        """
        message.respond('got it')
        
        return True