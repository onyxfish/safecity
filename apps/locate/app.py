import string

import rapidsms

from apps.locate.models import *

# Tokens
TOKEN_NONE = ''

TOKEN_SKIP_WORD = '<SKIP_WORD>'

TOKEN_ROAD = '<ROAD>'
TOKEN_ROAD_TYPE = '<ROAD_TYPE>'
TOKEN_DIRECTION = '<DIRECTION>'
TOKEN_NUMBER = '<NUMBER>'

TOKEN_AND = '<AND>'
TOKEN_BETWEEN = '<BETWEEN>'

TOKEN_ROAD_ARGS = '<ROAD_ARGS>'
TOKEN_BLOCK_NUMBER = '<BLOCK_NUMBER>'
 
class App(rapidsms.app.App):
    """
    This application attempts to exctract location information from the
    message and annotates the message object with that information.
    """
    SKIP_WORDS = []
    ROAD_TYPES = {}
    ROAD_DIRECTIONS = {}
    MAGIC_WORDS = {
        'AND': TOKEN_AND,
        '&': TOKEN_AND,
        'BETWEEN': TOKEN_BETWEEN,
        'BTWN': TOKEN_BETWEEN,
        'BTWEEN': TOKEN_BETWEEN,
    }
    
    def start(self):
        """
        Import English drop-words from file.
        """
        with open('data/wordlists/en-basic') as f:
            print 'Loading skip words'
            self.SKIP_WORDS = [word.upper() for word in f.readlines()]
        
        with open('data/streets/road_types.csv') as f:
            print 'Loading road types'
            for line in f.readlines():
                k, v = line.split(',')
                self.ROAD_TYPES[k] = v

        with open('data/streets/road_directions.csv') as f:
            print 'Loading road directions'
            for line in f.readlines():
                k, v = line.split(',')
                self.ROAD_DIRECTIONS[k] = v
    
    def parse(self, message):
        """
        Infer a location from the text, if possible and annotate it on
        the message object for use by other apps.
        """
        message.location = self._extract_location(message.text)
        
    def _extract_location(self, text):
        """
        Extract a location from a text string.
        """
        words = self._get_words_from_text(text)
        word_tokens = self._tokenize_words(words)
        location_tokens = self._substitute_road_args(word_tokens)
        location = self._determine_location(location_tokens)
        
        print location
        
        return location
        
    def _get_words_from_text(self, text):
        """
        Takes a raw message and returns a list of words prepared to
        be tokenized.
        """
        return self._strip_punctuation(text).upper().split()
        
    def _tokenize_words(self, words):
        """
        Take a list of prepped words and return a zip of words and
        their tokens.
        """
        word_count = len(words)
        word_tokens = [TOKEN_NONE for word in words]
                
        # Scan for magic (token) words
        for i in range(0, word_count):
            if words[i] in self.MAGIC_WORDS.keys():
                word_tokens[i] = self.MAGIC_WORDS[words[i]]
                
        # Scan for road directions
        for i in range(0, word_count):
            if words[i] in self.ROAD_DIRECTIONS.keys():
                word_tokens[i] = TOKEN_DIRECTION
                
        # Scan for road types
        for i in range(0, word_count):
            if words[i] in self.ROAD_TYPES.keys():
                word_tokens[i] = TOKEN_ROAD_TYPE

        # Scan for any obvious skip words
        for i in range(0, word_count):
            if word_tokens[i]:
                continue
                
            if words[i] in self.SKIP_WORDS:
                word_tokens[i] = TOKEN_SKIP_WORD
                
        # Scan for possible block numbers
        for i in range(0, word_count):
            if words[i].isdigit() and len(words[i]) <= 5:
                word_tokens[i] = TOKEN_NUMBER
        
        # Scan for road names
        for i in range(0, word_count):
            # Skip words that have already been tokenized
            if word_tokens[i]:
                continue
            
            roads = Road.objects.filter(name__exact=words[i])
            
            if roads:
                # At least one road has this name
                word_tokens[i] = TOKEN_ROAD
                
        return zip(words, word_tokens)
        
    def _substitute_road_args(self, word_tokens):
        """
        Takes a zip of words and tokens and generates a new zip containing
        only location specific tokens (TOKEN_ROAD_ARGS, TOKEN_AND, etc.)
        """
        word_count = len(word_tokens)
        new_tokens = []
        
        for i in range(0, word_count):
            word, token = word_tokens[i]
        
            if token == TOKEN_AND:
                new_tokens.append((word, TOKEN_AND))
                continue
            elif token == TOKEN_BETWEEN:
                new_tokens.append((word, TOKEN_BETWEEN))
                continue
            elif token != TOKEN_ROAD:
                continue
            
            road_prefix_direction = None
            road_name = word
            road_type = None
            road_suffix_direction = None
            block_number = None
        
            if i > 0:
                word, token = word_tokens[i - 1]
            
                if token == TOKEN_DIRECTION:
                    road_prefix_direction = word
                
                    if i - 1 > 0:
                        word, token = word_tokens[i - 2]
                    
                        if token == TOKEN_NUMBER:
                            # TODO - floor
                            block_number = word
                elif token == TOKEN_NUMBER:
                    # TODO - floor
                    block_number = word
                
            if i + 1 < word_count:
                word, token = word_tokens[i + 1]
            
                if token == TOKEN_ROAD_TYPE:
                    road_type = word
                
                    if i + 2 < word_count:
                        word, token = word_tokens[i + 2]
                    
                        if token == TOKEN_DIRECTION:
                            road_suffix_direction = word
                elif token == TOKEN_DIRECTION:
                    road_suffix_direction = word
        
            args = {'name': road_name}
            if road_prefix_direction: args['prefix_direction'] = road_prefix_direction
            if road_type: args['road_type'] = road_type
            if road_suffix_direction: args['suffix_direction'] = road_suffix_direction
            
            if block_number:
                new_tokens.append((block_number, TOKEN_BLOCK_NUMBER))
            
            new_tokens.append((args, TOKEN_ROAD_ARGS))
                
        return new_tokens
        
    def _determine_location(self, location_tokens):
        """
        Takes a fully-substituted string and attempts to determine an exact
        location.
        """
        args, pattern = zip(*location_tokens)
        
        print args
        print pattern
        
        if pattern == (TOKEN_ROAD_ARGS, TOKEN_ROAD_ARGS):
            oneway = args[0]
            otherway = args[1]
            return self._get_intersection(oneway, otherway)
        elif pattern == (TOKEN_ROAD_ARGS, TOKEN_AND, TOKEN_ROAD_ARGS):
            oneway = args[0]
            otherway = args[2]
            return self._get_intersection(oneway, otherway)
            
        return None
            
    def _get_intersection(self, oneway_args, otherway_args):
        """
        Tries various combination of name parameters in order to try to find
        a an intersection amongst the named roads
        """
        try_again = True
        
        while try_again:
            try_again = False
            
            print oneway_args, otherway_args
            
            oneway_set = Road.objects.filter(**oneway_args)
            otherway_set = Road.objects.filter(**otherway_args)
            
            def trim_arguments():
                # First try trimming suffix directions
                if 'suffix_direction' in oneway_args or 'suffix_direction' in otherway_args:
                    del oneway_args['suffix_direction']
                    del otherway_args['suffix_direction']
                    return True
                # Then try trimming prefix directions
                elif 'prefix_direction' in oneway_args or 'prefix_direction' in otherway_args:
                    del oneway_args['prefix_direction']
                    del otherway_args['prefix_direction']
                    return True
                # Lastly try trimming street types
                elif 'road_type' in oneway_args or 'road_type' in otherway_args:
                    del oneway_args['road_type']
                    del otherway_args['road_type']
                    return True
                else:
                    # Nothing left to try...
                    return False
            
            if not oneway_set or not otherway_set:
                try_again = trim_arguments()
                continue
            
            for oneway in oneway_set:    
                for otherway in otherway_set:
                    for one_intersection in oneway.intersections.all():
                        for other_intersection in otherway.intersections.all():
                            if one_intersection == other_intersection:
                                return one_intersection.location
                        
            try_again = trim_arguments()

        # No possible intersection of these two roads
        return None
        
    def _get_block(self, number, block):
        pass
        
    def _strip_punctuation(self, s):
        # All of string.punctuation except ampersand
        punc = '!"#$%\'()*+,-./:;<=>?@[\\]^_`{|}~'
        return s.translate(string.maketrans('',''), string.punctuation)
        