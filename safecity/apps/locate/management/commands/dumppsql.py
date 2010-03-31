from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option

import os
import re

import logging
log = logging.getLogger("newsapps.db.dumppsql")

SUBSTITUTION_PATTERN = re.compile("^(.+?')(.+?)(liblwgeom.+)$")

class Command(BaseCommand):
    """dump postgres database to sql file for News Apps"""
    option_list= BaseCommand.option_list + (
    make_option('-o', '--sql_output', type='string', action='store', dest='output',
        help='The output file where the SQL data will be dumped.',
        default="data/psql/dump.sql"),
    make_option('-r', '--reverse', type='string', action='store', dest='reverse',
        help='If specified, then the file at [output] will be processed to restore a prefix over $libdir (for Joes broken install)'),
    )


    def handle(self, *args, **options):
        #dump for deployment
        try:
            dumpfile = options['output']
            if options['reverse']:
                prefix = options['reverse']
                substitution(dumpfile,prefix)
                print "Rewrote %s using %s" % (dumpfile,prefix)
            else:
                if settings.DATABASE_USER:
                    os.system('pg_dump -U %s -O -x %s > %s' % (settings.DATABASE_USER,settings.DATABASE_NAME,dumpfile))
                else:
                    os.system('pg_dump -O -x %s > %s' % (settings.DATABASE_NAME,dumpfile))
                substitution(dumpfile,'$libdir/')
                print('sql dumped to: %s' % dumpfile)
        except KeyError:
            print("You must specify the SQL output file using -o or --sql_output.")
            
def substitution(fname,prefix):
    if not prefix.endswith("/"):
        prefix += "/"
    lines = []    
    for line in open(fname).readlines():
        lines.append(fix_line(line,prefix))
    out = open(fname,"w")
    for line in lines:
        out.write(line)
    out.close()    

def fix_line(line,prefix):
    parts = SUBSTITUTION_PATTERN.split(line)
    if len(parts) == 1:
        return parts[0]
    else:
        parts = parts[1:-1]    
        parts[1] = prefix
        return "".join(parts)
    
