import rapidsms

from apps.locate.models import *

class App (rapidsms.app.App):
    """
    This application attempts to exctract location information from the
    message and annotates the message object with that information.
    """
    def parse (self, message):
        """
        Infer a location from the text, if possible.
        """
        message.location = self.extract_location(message.text)
        
def extract_location(text):
    """
    Extract a location from a text string.
    
    TODO
    """
    return None