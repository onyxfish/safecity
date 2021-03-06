import os
import re
import string

from django.conf import settings

from safecity.apps.locate.models import *

# Regexes
PUNCTUATION_REGEX = re.compile('[\!\"\#\$\%\\\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\]\^\_\`\{\|\}\~]+')
WHITESPACE_REGEX = re.compile('\s+')

# Tokens
TOKEN_NONE = ''

TOKEN_SKIP_WORD = '<SKIP_WORD>'

TOKEN_ROAD = '<ROAD>'
TOKEN_ROAD_TYPE = '<ROAD_TYPE>'
TOKEN_DIRECTION = '<DIRECTION>'
TOKEN_NUMBER = '<NUMBER>'

TOKEN_AND = '<AND>'
TOKEN_BETWEEN = '<BETWEEN>'
TOKEN_BLOCK_OF = '<BLOCK_OF>'

TOKEN_ROAD_ARGS = '<ROAD_ARGS>'
TOKEN_BLOCK_NUMBER = '<BLOCK_NUMBER>'

class NoLocationException(Exception):
    pass

class MultiplePossibleLocationsException(Exception):
    pass
    
class RoadWithoutBlockException(Exception):
    pass
    
def find_sub_sequences(needle, haystack):
    """
    Find any number of occurences of list 'needle' inside within list
    'haystack.'
    
    Via Derek Martin:
    http://bytes.com/topic/python/answers/836221-test-if-list-contains-another-list
    """
    results = []
    needle_len = len(needle)
    for i in range(len(haystack)):
        if haystack[i:i+needle_len] == needle:
            results.append(i)
            return results
            
def strip_punctuation(text):
    return PUNCTUATION_REGEX.sub(' ', text)
 
class LocationParser(object):
    """
    This object encapsulates the logic for parsing locations from text.
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
        'BLOCKOF': TOKEN_BLOCK_OF,  # See note in _get_words_from_text()
    }
    
    def __init__(self):
        """
        Build word and token sets.
        """
        with open(os.path.join(settings.DATA_DIR, 'wordlists/skipwords')) as f:
            self.SKIP_WORDS = [word for word in f.readlines()]
        
        with open(os.path.join(settings.DATA_DIR, 'streets/road_types.csv')) as f:
            for line in f.readlines():
                k, v = line.split(',')
                self.ROAD_TYPES[k] = v

        with open(os.path.join(settings.DATA_DIR, 'streets/road_directions.csv')) as f:
            for line in f.readlines():
                k, v = line.split(',')
                self.ROAD_DIRECTIONS[k] = v
        
    def extract_location(self, text):
        """
        Extract a location from a text string.
        
        This is a four stage process:
        1) Extract words from the text.
        2) Tokenize the words, identifying road names, etc.
        3) Extract location arguments from tokens.
        4) Attempt to pinpoint an exact location using extracted arguments.
        
        If searches using all parsed arguments fail the parser will "fall
        back" to progressively simpler searches in an attempt to find a match.
        """
        words = self._get_words_from_text(text)
        word_tokens = self._tokenize_words(words)
        location_tokens = self._substitute_road_args(word_tokens)
        
        if not location_tokens:
            raise NoLocationException()
        
        return self._determine_location(location_tokens)
        
    def _get_words_from_text(self, text):
        """
        Takes a raw message and returns a list of words prepared to
        be tokenized.
        """
        text = text.upper()
        text = strip_punctuation(text)
        text = text.strip()
        
        # Manual hack to handle the only two-word magic string
        text = text.replace('BLOCK OF', 'BLOCKOF')
        
        words = WHITESPACE_REGEX.split(text)
        return words
        
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
        
        # Scan for single-word road names
        for i in range(0, word_count):
            # Skip words that have already been tokenized
            if word_tokens[i]:
                continue
            
            try:
                # Attempt to grab an alias with this exact spelling
                alias = RoadAlias.objects.get(name__exact=words[i])
                
                # At least one road has this name
                word_tokens[i] = TOKEN_ROAD
                
                # Rewrite the token with the canonical name
                words[i] = alias.fetch_canonical_name()
            except RoadAlias.DoesNotExist:
                continue
                
        # Scan for multi-word road names
        for i in range(0, word_count):
            # Skip words that have already been tokenized
            try:
                if word_tokens[i]:
                    continue
            except IndexError:
                # Overshot end of words because some were deleted
                # (this is good, it means we found something)
                continue
            
            j = 1
            
            try:
                while not word_tokens[i + j]:
                    phrase = ' '.join(words[i:i + j + 1])

                    try:
                        alias = RoadAlias.objects.get(name__exact=phrase)

                        words[i] = alias.fetch_canonical_name()
                        word_tokens[i] = TOKEN_ROAD

                        del words[i+1:i+j+1]
                        del word_tokens[i+1:i+j+1]
                        
                        break
                    except RoadAlias.DoesNotExist:
                        pass
                    
                    j += 1
            except IndexError:
                # End of words
                pass
                
        return zip(words, word_tokens)
        
    def _substitute_road_args(self, word_tokens):
        """
        Takes a zip of words and tokens and generates a new zip containing
        only location specific tokens (TOKEN_BLOCK_NUMBER, TOKEN_ROAD_ARGS,
        etc.)
        
        TODO: rework with XML-style annotated strings? Pyparsing?
        """
        word_count = len(word_tokens)
        new_tokens = []
        
        for i in range(0, word_count):
            word, token = word_tokens[i]
        
            if token != TOKEN_ROAD:
                continue
            
            road_prefix_direction = None
            road_name = word
            road_type = None
            road_suffix_direction = None
            block_number = None
        
            if i > 0:
                word, token = word_tokens[i - 1]
            
                # North Austin
                if token == TOKEN_DIRECTION:
                    road_prefix_direction = word
                
                    if i - 1 > 0:
                        word, token = word_tokens[i - 2]
                    
                        # 5300 N Austin
                        if token == TOKEN_NUMBER:
                            block_number = Block.to_block_number(int(word))
                        # Block of Austin
                        elif token == TOKEN_BLOCK_OF:
                            if i - 2 > 0:
                                word, token = word_tokens[i - 3]

                                # 5300 Block of N Austin
                                if token == TOKEN_NUMBER:
                                    block_number = Block.to_block_number(int(word))
                # Block of Austin
                elif token == TOKEN_BLOCK_OF:
                    if i - 1 > 0:
                        word, token = word_tokens[i - 2]

                        # 5300 Block of Austin
                        if token == TOKEN_NUMBER:
                            block_number = Block.to_block_number(int(word))
                # 5300 Austin
                elif token == TOKEN_NUMBER:
                    block_number = Block.to_block_number(int(word))
                
            if i + 1 < word_count:
                word, token = word_tokens[i + 1]
            
                # Austin Ave
                if token == TOKEN_ROAD_TYPE:
                    road_type = word
                
                    if i + 2 < word_count:
                        word, token = word_tokens[i + 2]
                    
                        # Austin Ave N
                        if token == TOKEN_DIRECTION:
                            road_suffix_direction = word
                # Austin N
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
        location = None
        args, pattern = zip(*location_tokens)
        
        if pattern == (TOKEN_ROAD_ARGS, TOKEN_ROAD_ARGS):
            location = self._get_intersection(args[0], args[1])
        elif pattern == (TOKEN_BLOCK_NUMBER, TOKEN_ROAD_ARGS):
            location = self._get_block(args[0], args[1])
        elif pattern == (TOKEN_ROAD_ARGS,):
            raise RoadWithoutBlockException()
            
        if location == None:
            raise NoLocationException()
            
        return location
            
    def _get_intersection(self, oneway_args, otherway_args):
        """
        Try various combination of name parameters in order to try to find
        an intersection amongst the named roads.
        """
        try_again = True
        
        while try_again:
            try_again = False
            
            oneway_set = Road.objects.filter(**oneway_args)
            otherway_set = Road.objects.filter(**otherway_args)
            
            def trim_arguments():
                # First try trimming suffix directions
                if 'suffix_direction' in oneway_args or 'suffix_direction' in otherway_args:
                    if 'suffix_direction' in oneway_args: del oneway_args['suffix_direction']
                    if 'suffix_direction' in otherway_args: del otherway_args['suffix_direction']
                    return True
                # Then try trimming prefix directions
                elif 'prefix_direction' in oneway_args or 'prefix_direction' in otherway_args:
                    if 'prefix_direction' in oneway_args: del oneway_args['prefix_direction']
                    if 'prefix_direction' in otherway_args: del otherway_args['prefix_direction']
                    return True
                # Lastly try trimming street types
                elif 'road_type' in oneway_args or 'road_type' in otherway_args:
                    if 'road_type' in oneway_args: del oneway_args['road_type']
                    if 'road_type' in otherway_args: del otherway_args['road_type']
                    return True
                else:
                    # Nothing left to try...
                    return False
            
            if not oneway_set or not otherway_set:
                try_again = trim_arguments()
                continue
            
            # Search for a shared intersection amongst all possible combinations
            possible_intersections = []
            
            for oneway in oneway_set:    
                for otherway in otherway_set:
                    for one_intersection in oneway.intersections.all():
                        for other_intersection in otherway.intersections.all():
                            if one_intersection == other_intersection:
                                # Careful not to add the same intersection twice
                                if one_intersection not in possible_intersections:
                                    possible_intersections.append(one_intersection)
                                
            if len(possible_intersections) == 1:
                # Yay!
                return possible_intersections[0]
            elif len(possible_intersections) > 1:
                # Not enough information to get an exact match
                raise MultiplePossibleLocationsException()
                        
            try_again = trim_arguments()

        # No possible intersection of these two roads
        return None
        
    def _get_block(self, number, road_args):
        """
        Try various combinations of name parameters in order to find a
        block of the given number on the named road.
        """
        try_again = True
        
        while try_again:
            try_again = False
            
            road_set = Road.objects.filter(**road_args)
            
            def trim_arguments():
                # First try trimming suffix directions
                if 'suffix_direction' in road_args:
                    del road_args['suffix_direction']
                    return True
                # Then try trimming prefix directions
                elif 'prefix_direction' in road_args:
                    del road_args['prefix_direction']
                    return True
                # Lastly try trimming street types
                elif 'road_type' in road_args:
                    del road_args['road_type']
                    return True
                else:
                    # Nothing left to try...
                    return False
            
            if not road_set:
                try_again = trim_arguments()
                continue
            
            # Search for block with this number amongst the possibilities
            possible_blocks = []
            
            for road in road_set:
                try:
                    possible_blocks.append(Block.objects.get(number=number, road=road))
                except Block.DoesNotExist:
                    continue
                                
            if len(possible_blocks) == 1:
                # Yay!
                return possible_blocks[0]
            elif len(possible_blocks) > 1:
                # Not enough information to get an exact match
                raise MultiplePossibleLocationsException()
                        
            try_again = trim_arguments()

        # No block of this number on a road of this name
        return None
