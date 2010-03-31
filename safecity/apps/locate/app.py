import string

import rapidsms

from apps.locate.location_parser import *
from apps.priorities import PRIORITIES
 
class App(rapidsms.app.App):
    """
    This application attempts to exctract location information from the
    message and annotates the message object with that information.
    """
    PRIORITY = PRIORITIES['locate']
    
    def start(self):
        """
        Import English drop-words from file.
        """
        self.parser = LocationParser()
    
    def parse(self, message):
        """
        Infer a location from the text, if possible, and annotate it on
        the message object for use by other apps.
        """
        try:
            message.location = self.parser.extract_location(message.text)
        except NoLocationException:
            # TODO
            pass
        except MultiplePossibleLocationsException:
            # TODO
            pass
        except RoadWithoutBlockException:
            # TODO
            pass
        
        # TODO: debug
        if hasattr(message, 'location'):
            message.respond(str(message.location))