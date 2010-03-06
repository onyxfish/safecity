import logging
log = logging.getLogger('safecity.locate.load_streets')
from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from apps.locate.models import Location

MAPPING_FILE = 'data/electionnight/race_mappings.csv'

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
        
        pass