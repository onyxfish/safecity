import logging
log = logging.getLogger("safecity.locate.load_srids")
from optparse import make_option
import os

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection, transaction, IntegrityError

DATA_DIR = 'data/projections'

class Command(NoArgsCommand):
    title = 'locate.load_srids'
    help = 'Loads required SRID definitions into PostGIS.'

    def handle_noargs(self, **options):
        log.info('Loading SRIDs.')
        
        for filename in os.listdir(DATA_DIR):
            with open(os.path.join(DATA_DIR, filename), 'r') as f:
                sql = f.read()
        
            try:
                cursor = connection.cursor()
                cursor.execute(sql)
                transaction.commit_unless_managed()
                log.info('%s successfully loaded.' % filename)
            except IntegrityError:
                log.info('%s already loaded.' % filename)
        
        log.info('Finished.')