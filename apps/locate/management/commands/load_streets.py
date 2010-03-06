import csv
import logging
log = logging.getLogger('safecity.locate.load_streets')
from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from apps.locate.models import Location

DATA_DIR = 'data/streets'

class Command(NoArgsCommand):
    help = 'Import street locations into the database using the Django models.'

    option_list = NoArgsCommand.option_list + (
        make_option('-c', '--clear', action='store_true', dest='clear',
            help='Clear all street locations from the DB.'),
        )

    def handle_noargs(self, **options):
        if options['clear']:
            logging.info("Clearing all street locations.")
            Location.objects.filter(locale__in=['CR', 'ST']).delete()
        
        with open(os.path.join(DATA_DIR, 'names.csv'), 'r') as f:
            data = csv.read(f)
            data.next() # header
            
            for row in data:
                self.process_street(row)
                
        with open(os.path.join(DATA_DIR, 'aliases.csv'), 'r') as f:
            data = csv.read(f)
            data.next() # header

            for row in data:
                self.process_alias(row)   
                
    def process_street(row):
        """
        TODO
        """
        pass
        
    def process_alias(row):
        """
        TODO
        """
        pass
        
        