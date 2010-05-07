import csv
import logging
log = logging.getLogger("safecity.locate.load_aliases")
from optparse import make_option
import os

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from safecity.apps.locate.location_parser import strip_punctuation, WHITESPACE_REGEX
from safecity.apps.locate.models import *

ROADS_CSV = 'data/streets/names.csv'
ALIASES_CSV = 'data/streets/aliases.csv'

ALIAS_TYPES = {
    'ALIAS': 'AL',
    'HONORARY': 'HN',
    '911': 'EM',
    'NAMING_CONV': 'NC',
}

class Command(NoArgsCommand):
    title = 'locate.load_centerline'
    help = 'Import road alias data into the database using the Django models.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all centerline data from the DB.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            log.info('Clearing all aliases.')
            RoadAlias.objects.all().delete()
        
        log.info('Creating canonical aliases.')
        
        for road in Road.objects.all():
            try:
                alias = RoadAlias.objects.get(
                    name=road.name,
                    alias_type='CA'
                )
            except RoadAlias.DoesNotExist:
                # Create canonical alias--exactly the original name
                alias = RoadAlias.objects.create(
                    name=road.name,
                    alias_type='CA'
                )
                
            alias.roads.add(road)
            
        log.info('Loading alias tables.')
        
        id_name_mapping = {}
            
        reader = csv.DictReader(open(ROADS_CSV, 'r'))
        
        for row in reader:
            id_name_mapping[row['Street_ID']] = row['Street Name']
            
        reader = csv.DictReader(open(ALIASES_CSV, 'r'))
        
        for row in reader:
            canonical_name = id_name_mapping[row['Base_Street_ID']]
            alias_type = ALIAS_TYPES[row['Alias Type']]
            alias_name = self.format_alias_name(row['Street Name'])
            
            try:
                canonical_alias = RoadAlias.objects.get(
                    name=canonical_name,
                    alias_type='CA'
                )
            except RoadAlias.DoesNotExist:
                log.debug('Skipping alias for "%s"--no such road.' % canonical_name)
                continue
            
            try:
                new_alias = RoadAlias.objects.get(
                    name=alias_name
                )
                
                log.debug('Skipping duplicate alias: %s (type %s). Storied type is %s.' % (alias_name, alias_type, new_alias.alias_type))
                continue
            except RoadAlias.DoesNotExist:
                new_alias = RoadAlias.objects.create(
                    name=alias_name,
                    alias_type=alias_type
                )
            
            for road in canonical_alias.roads.all():
                new_alias.roads.add(road)
                
            log.debug('Created alias %s for %s' % (alias_name, canonical_name))
            
    def format_alias_name(self, name):
        """
        Handles stripping punctuation and formatting whitespace.
        """
        result = strip_punctuation(name)
        result = WHITESPACE_REGEX.sub(' ', result)
        return result