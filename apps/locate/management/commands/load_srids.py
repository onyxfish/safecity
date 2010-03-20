from optparse import make_option
import os

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection, transaction, IntegrityError

from rapidsms.log import Logger
log = Logger(level='Debug')

DATA_DIR = 'data/projections'

class Command(NoArgsCommand):
    title = 'locate.load_srids'
    help = 'Loads required SRID definitions into PostGIS.'

    def handle_noargs(self, **options):
        log.write(self, 'INFO', 'Loading SRIDs.')
        
        for filename in os.listdir(DATA_DIR):
            with open(os.path.join(DATA_DIR, filename), 'r') as f:
                sql = f.read()
        
            try:
                cursor = connection.cursor()
                cursor.execute(sql)
                transaction.commit_unless_managed()
                log.write(self, 'INFO', '%s successfully loaded.' % filename)
            except IntegrityError:
                log.write(self, 'INFO', '%s already loaded.' % filename)
        
        log.write(self, 'INFO', 'Finished.')