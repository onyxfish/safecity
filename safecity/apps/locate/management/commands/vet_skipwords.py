import csv
import logging
log = logging.getLogger("safecity.locate.vet_skip_words")
from optparse import make_option
import os
import re

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from safecity.apps.locate.location_parser import strip_punctuation, WHITESPACE_REGEX
from safecity.apps.locate.models import *
from safecity.apps.tropo.views import KEYWORDS

class Command(NoArgsCommand):
    title = 'locate.vet_skip_words'
    help = 'Verify that no skip_words are road names or other keywords.'

    def handle_noargs(self, **options):
        skip_words = []
        
        with open(os.path.join(settings.DATA_DIR, 'wordlists/skipwords')) as f:
            skip_words = [word.strip() for word in f.readlines()]
            
        road_types = []
            
        with open(os.path.join(settings.DATA_DIR, 'streets/road_types.csv')) as f:
            for line in f.readlines():
                k, v = line.split(',')
                road_types.append(k)

        road_directions = []

        with open(os.path.join(settings.DATA_DIR, 'streets/road_directions.csv')) as f:
            for line in f.readlines():
                k, v = line.split(',')
                road_directions.append(k)
        
        keywords = []
                
        for v in KEYWORDS.values():
            keywords.extend(v)

        rewrite = skip_words
        
        for word in skip_words:
            # Check against road types
            if word in road_types:
                log.error('Word "%s" is also a road type.' % word)
                rewrite.remove(word)
                continue
                
            if word in road_directions:
                log.error('Word "%s" is also a road direction.' % word)
                rewrite.remove(word)
                continue
                
            if word in keywords:
                log.error('Word "%s" is also a keyword.' % word)
                rewrite.remove(word)
                continue
            
            like_aliases = RoadAlias.objects.filter(name__contains=word)
            
            if like_aliases:
                regex = re.compile('\\b%s\\b' % word)
                
                for alias in like_aliases:
                    if regex.search(alias.name):
                        log.error('Word "%s" is also a part of road alias "%s".' % (word, alias.name))
                        rewrite.remove(word)
                        break
                        
        log.info('Rewriting skip_words list without problem words')
        
        with open(os.path.join(settings.DATA_DIR, 'wordlists/skipwords')) as f:
            f.write('\n'.join(rewrite))