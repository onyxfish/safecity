import string

import rapidsms

from apps.locate.models import *

class App(rapidsms.app.App):
    """
    This application attempts to exctract location information from the
    message and annotates the message object with that information.
    """
    DROP_WORDS = []
    
    def start(self):
        """
        Import English drop-words from file.
        
        TODO: verify these are loaded only once
        """
        with open('data/wordlists/en-basic') as f:
            print 'Loading dropwords'
            DROP_WORDS = [word.lower() for word in f.readlines()]
    
    def parse(self, message):
        """
        Infer a location from the text, if possible and annotate it on
        the message object for use by other apps.
        """
        message.location = self._extract_location(message.text)
        
    def _extract_location(self, text):
        """
        Extract a location from a text string.
    
        TODO
        """
        words = text.split()
        words_to_check = [word for word in words if word not in self.DROP_WORDS]
        
        roads = []
        for word in words:
            w = self._strip_punctuation(word)
            
            if w.isdigit():
                continue
            
            try:
                roads.append(Road.objects.get(name__iexact=w))
            except Road.DoesNotExist:
                pass
        
        if len(roads) == 2:
            for i in roads[0].intersections.all():
                if roads[1] in i.roads.all():
                    return i.location
        
        return None
        
    def _strip_punctuation(self, s):
        return s.translate(string.maketrans("",""), string.punctuation)
        